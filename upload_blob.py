"""
Unggah video yang dirujuk halaman trip ke Vercel Blob.

Video tidak ikut ke GitHub (berkasnya jauh di atas batas 100 MB per file yang
dipaksakan GitHub), jadi halaman memanggilnya lewat URL Blob. Skrip ini yang
mengisi gudangnya.

Cara pakai:
    python upload_blob.py            # unggah yang belum ada
    python upload_blob.py --dry      # lihat rencananya saja, tanpa mengunggah

Aman dijalankan ulang: berkas yang sudah ada di Blob dengan ukuran sama akan
dilewati, jadi unggahan yang putus di tengah tinggal dijalankan lagi.

Syarat:
    - Vercel CLI terpasang dan sudah `vercel login`
    - Folder ini sudah `vercel link` ke proyek jelajahwisatasumatera
      (itu yang mengisi BLOB_READ_WRITE_TOKEN di .env.local)

PENTING soal kuota: paket Hobby cuma memberi 1 GB untuk SELURUH video. Skrip
menolak jalan kalau total melewatinya, karena kalau dipaksa Vercel akan
menghentikan unggahan di tengah dengan "Storage quota exceeded" — sebagian
video hidup, sebagian mati, tanpa peringatan. Lebih baik ketahuan di awal.
"""

import os
import re
import subprocess
import sys
import urllib.request

BASE_VIDEO = "https://qubhiargbkwdxwbe.public.blob.vercel-storage.com"

# Batas simpanan paket Hobby. Naikkan kalau sudah pindah ke paket berbayar.
#
# PENTING — ini desimal (1 GB = 1.000.000.000 byte), bukan 1024^3.
# Vercel menghitung begitu: waktu berkas lokal berjumlah 918 MiB, dashboard
# menulis 962 MB. Dulu di sini tertulis 1024^3, yang memberi kelonggaran 74 MB
# di atas batas asli — cukup untuk membuat unggahan berhenti di tengah padahal
# skrip bilang masih muat.
BATAS_BYTE = 1_000_000_000

# Di atas ini skrip tetap jalan tapi memperingatkan. Menambah satu video 1080p
# biasanya 30-100 MB, jadi ambang ini memberi aba-aba sebelum benar-benar mepet.
AMBANG_WASPADA = 0.80


def mb(n):
    """MB desimal — satuan yang sama dengan yang ditampilkan dashboard Vercel."""
    return n / 1_000_000


def baca_token():
    """Ambil BLOB_READ_WRITE_TOKEN dari .env.local (diisi otomatis oleh vercel link)."""
    token = os.environ.get('BLOB_READ_WRITE_TOKEN')
    if token:
        return token
    try:
        with open('.env.local', encoding='utf-8') as f:
            for baris in f:
                if baris.startswith('BLOB_READ_WRITE_TOKEN='):
                    return baris.split('=', 1)[1].strip().strip('"')
    except FileNotFoundError:
        pass
    return None


def daftar_video():
    """Semua berkas .mp4 yang dirujuk halaman trip, tanpa duplikat, urut."""
    ditemukan = set()
    for nama in os.listdir('.'):
        if re.fullmatch(r'trip-.*\.html', nama):
            with open(nama, encoding='utf-8') as f:
                ditemukan.update(re.findall(r'assets/[^"#]*?\.mp4', f.read()))
    return sorted(ditemukan)


def ukuran_di_blob(path):
    """Ukuran berkas di Blob, atau None kalau belum ada."""
    req = urllib.request.Request(f"{BASE_VIDEO}/{path}", method='HEAD')
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return int(r.headers.get('Content-Length', 0))
    except Exception:
        return None


def unggah(path, token):
    cmd = ['vercel', 'blob', 'put', path,
           '--access', 'public',
           '--pathname', path,
           '--allow-overwrite', 'true',
           '--multipart', 'true',
           '--content-type', 'video/mp4',
           '--rw-token', token]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL,
                       stderr=subprocess.PIPE, shell=(os.name == 'nt'))
        return None
    except subprocess.CalledProcessError as e:
        pesan = e.stderr.decode(errors='ignore').strip().splitlines()
        return pesan[-1] if pesan else 'gagal tanpa keterangan'
    except FileNotFoundError:
        return 'vercel CLI tidak ditemukan di PATH'


def main():
    dry = '--dry' in sys.argv

    berkas = daftar_video()
    if not berkas:
        print("Tidak ada video yang dirujuk halaman trip-*.html.")
        return 1

    hilang = [f for f in berkas if not os.path.exists(f)]
    if hilang:
        print(f"! {len(hilang)} berkas dirujuk halaman tapi tidak ada di komputer ini:")
        for f in hilang:
            print(f"    {f}")
        print("  Jalankan prepare_assets.py dulu untuk membuatnya.")
        return 1

    total = sum(os.path.getsize(f) for f in berkas)
    sisa = BATAS_BYTE - total
    pakai = total / BATAS_BYTE

    print(f"{len(berkas)} video dirujuk halaman, total {mb(total):.0f} MB "
          f"dari batas {mb(BATAS_BYTE):.0f} MB ({pakai*100:.0f}%).")
    print(f"Sisa ruang: {mb(sisa):.0f} MB "
          f"— kira-kira muat {int(mb(sisa) // 60)} video 1080p lagi.")

    if total > BATAS_BYTE:
        print(f"\n! Kelebihan {mb(-sisa):.0f} MB. Unggahan akan berhenti di tengah "
              f"kalau dipaksa, sebagian video hidup sebagian mati.")
        print("  Kecilkan dulu yang paling boros:")
        for f in sorted(berkas, key=os.path.getsize, reverse=True)[:3]:
            print(f"    {mb(os.path.getsize(f)):6.0f} MB  {f}")
        return 1

    if pakai >= AMBANG_WASPADA:
        print(f"\n! Sudah {pakai*100:.0f}% dari batas. Yang paling boros:")
        for f in sorted(berkas, key=os.path.getsize, reverse=True)[:3]:
            print(f"    {mb(os.path.getsize(f)):6.0f} MB  {f}")
        print("  Kecilkan salah satunya sebelum menambah video baru.")

    token = baca_token()
    if not token and not dry:
        print("\n! BLOB_READ_WRITE_TOKEN tidak ketemu di .env.local.")
        print("  Jalankan: vercel link")
        return 1

    print()
    naik = lewat = gagal = 0
    for f in berkas:
        lokal = os.path.getsize(f)
        jauh = ukuran_di_blob(f)

        if jauh == lokal:
            print(f"  lewat   {f:<34} {mb(lokal):.0f} MB sudah ada")
            lewat += 1
            continue

        if dry:
            print(f"  unggah  {f:<34} {mb(lokal):.0f} MB")
            naik += 1
            continue

        print(f"  unggah  {f:<34} {mb(lokal):.0f} MB ... ", end='', flush=True)
        galat = unggah(f, token)
        if galat:
            print("GAGAL")
            print(f"          {galat}")
            gagal += 1
        else:
            print("selesai")
            naik += 1

    print(f"\nTerunggah: {naik}   Dilewati: {lewat}   Gagal: {gagal}")
    return 1 if gagal else 0


if __name__ == '__main__':
    sys.exit(main())
