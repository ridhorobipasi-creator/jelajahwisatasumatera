"""
Unggah video yang dirujuk halaman trip ke Cloudflare R2.

Pengganti upload_blob.py. Alasan pindah: Vercel Blob paket Hobby memberi 10 GB
transfer per bulan, dan pada 2026-08-02 situs ini memakai 21,4 GB dalam 5 hari
sehingga seluruh store diblokir — semua video mati serentak. R2 tidak menagih
transfer keluar sama sekali, jadi masalah itu tidak bisa terulang. Simpanan
gratisnya 10 GB, sepuluh kali lipat Blob.

Cara pakai:
    python upload_r2.py            # unggah yang belum ada
    python upload_r2.py --dry      # lihat rencananya saja, tanpa mengunggah

Aman dijalankan ulang: berkas yang sudah ada di R2 dengan ukuran sama dilewati,
jadi unggahan yang putus di tengah tinggal dijalankan lagi.

Syarat — isi di .env.local (sudah di-gitignore, jangan pernah di-commit):
    R2_ACCOUNT_ID=...
    R2_ACCESS_KEY_ID=...
    R2_SECRET_ACCESS_KEY=...
    R2_BUCKET=jelajahwisata-video

Ambil ketiganya dari Cloudflare: R2 -> Manage API Tokens -> Create,
izin "Object Read & Write", dibatasi ke bucket itu saja.
"""

import datetime
import hashlib
import hmac
import os
import re
import sys
import urllib.parse

try:
    import requests
except ImportError:
    requests = None

# Alamat publik video — subdomain yang ditempelkan ke bucket R2.
# Harus sama dengan BASE_VIDEO di build_trip.py.
BASE_VIDEO = "https://video.jelajahwisatasumatera.my.id"

# Jatah simpanan gratis R2. Transfer keluar tidak ditagih, jadi tidak ada
# yang perlu dijaga di sisi itu — beda dengan Blob dulu.
BATAS_BYTE = 10_000_000_000
AMBANG_WASPADA = 0.80

WILAYAH = 'auto'          # R2 selalu 'auto'
LAYANAN = 's3'


def mb(n):
    """MB desimal, satuan yang dipakai dashboard Cloudflare."""
    return n / 1_000_000


# ── Konfigurasi ───────────────────────────────────────────────────────

def baca_env():
    """Ambil setelan dari lingkungan, lalu dari .env.local sebagai cadangan."""
    kunci = ('R2_ACCOUNT_ID', 'R2_ACCESS_KEY_ID', 'R2_SECRET_ACCESS_KEY', 'R2_BUCKET')
    setelan = {k: os.environ.get(k) for k in kunci}
    try:
        with open('.env.local', encoding='utf-8') as f:
            for baris in f:
                baris = baris.strip()
                if not baris or baris.startswith('#') or '=' not in baris:
                    continue
                k, v = baris.split('=', 1)
                k = k.strip()
                if k in kunci and not setelan.get(k):
                    setelan[k] = v.strip().strip('"').strip("'")
    except FileNotFoundError:
        pass
    return setelan


# ── Penandatanganan AWS SigV4 (R2 memakai protokol S3) ────────────────
#
# Ditulis tangan supaya tidak perlu memasang boto3. Urutannya baku dan
# tidak boleh diubah: salah satu spasi saja membuat tanda tangannya ditolak.

def _hmac(kunci, pesan):
    return hmac.new(kunci, pesan.encode('utf-8'), hashlib.sha256).digest()


def _kunci_tanda_tangan(rahasia, tanggal):
    k = _hmac(f'AWS4{rahasia}'.encode('utf-8'), tanggal)
    k = _hmac(k, WILAYAH)
    k = _hmac(k, LAYANAN)
    return _hmac(k, 'aws4_request')


def sha256_berkas(path):
    """Hash isi berkas tanpa memuat seluruhnya ke memori."""
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for blok in iter(lambda: f.read(1 << 20), b''):
            h.update(blok)
    return h.hexdigest()


def tanda_tangani(metode, host, jalur, setelan, sha, tipe=None, panjang=None):
    """Susun header Authorization untuk satu permintaan."""
    sekarang = datetime.datetime.now(datetime.timezone.utc)
    amzdate = sekarang.strftime('%Y%m%dT%H%M%SZ')
    tanggal = sekarang.strftime('%Y%m%d')

    header = {
        'host': host,
        'x-amz-content-sha256': sha,
        'x-amz-date': amzdate,
    }
    if tipe:
        header['content-type'] = tipe

    urut = sorted(header)
    header_kanonik = ''.join(f'{k}:{header[k]}\n' for k in urut)
    daftar_header = ';'.join(urut)

    # Tiap ruas jalur di-encode, tapi garis miringnya dibiarkan
    jalur_kanonik = '/' + '/'.join(
        urllib.parse.quote(r, safe='') for r in jalur.lstrip('/').split('/'))

    permintaan_kanonik = '\n'.join(
        [metode, jalur_kanonik, '', header_kanonik, daftar_header, sha])

    lingkup = f'{tanggal}/{WILAYAH}/{LAYANAN}/aws4_request'
    untuk_ditandatangani = '\n'.join([
        'AWS4-HMAC-SHA256',
        amzdate,
        lingkup,
        hashlib.sha256(permintaan_kanonik.encode('utf-8')).hexdigest(),
    ])

    tanda = hmac.new(
        _kunci_tanda_tangan(setelan['R2_SECRET_ACCESS_KEY'], tanggal),
        untuk_ditandatangani.encode('utf-8'), hashlib.sha256).hexdigest()

    header['Authorization'] = (
        f"AWS4-HMAC-SHA256 Credential={setelan['R2_ACCESS_KEY_ID']}/{lingkup}, "
        f"SignedHeaders={daftar_header}, Signature={tanda}")
    if panjang is not None:
        header['content-length'] = str(panjang)
    return header


def alamat(setelan, kunci):
    host = f"{setelan['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com"
    jalur = f"/{setelan['R2_BUCKET']}/{kunci}"
    return host, jalur, f"https://{host}{jalur}"


# ── Operasi ───────────────────────────────────────────────────────────

def daftar_video():
    """Semua .mp4 yang dirujuk halaman trip, tanpa duplikat, urut."""
    ditemukan = set()
    for nama in os.listdir('.'):
        if re.fullmatch(r'trip-.*\.html', nama):
            with open(nama, encoding='utf-8') as f:
                ditemukan.update(re.findall(r'assets/[^"#]*?\.mp4', f.read()))
    return sorted(ditemukan)


def ukuran_di_r2(setelan, kunci):
    """Ukuran objek di R2, atau None kalau belum ada."""
    host, jalur, url = alamat(setelan, kunci)
    kosong = hashlib.sha256(b'').hexdigest()
    header = tanda_tangani('HEAD', host, jalur, setelan, kosong)
    try:
        r = requests.head(url, headers=header, timeout=30)
        if r.status_code == 200:
            return int(r.headers.get('Content-Length', 0))
    except requests.RequestException:
        pass
    return None


def unggah(setelan, path):
    """PUT satu berkas. Mengembalikan None kalau berhasil, pesan kalau gagal."""
    host, jalur, url = alamat(setelan, path)
    sha = sha256_berkas(path)
    besar = os.path.getsize(path)
    header = tanda_tangani('PUT', host, jalur, setelan, sha,
                           tipe='video/mp4', panjang=besar)
    try:
        with open(path, 'rb') as f:
            r = requests.put(url, headers=header, data=f, timeout=600)
        if r.status_code in (200, 201):
            return None
        pesan = re.sub(r'<[^>]+>', ' ', r.text or '').strip()
        return f"HTTP {r.status_code} {pesan[:200]}"
    except requests.RequestException as e:
        return str(e)[:200]


def main():
    dry = '--dry' in sys.argv

    if requests is None:
        print("! Modul 'requests' belum terpasang. Jalankan: pip install requests")
        return 1

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
    bagian = total / BATAS_BYTE

    print(f"{len(berkas)} video dirujuk halaman, total {mb(total):.0f} MB "
          f"dari jatah gratis {mb(BATAS_BYTE):.0f} MB ({bagian*100:.0f}%).")
    print(f"Sisa ruang: {mb(sisa):.0f} MB.")
    print("Transfer keluar tidak ditagih R2, jadi tidak ada kuota tontonan "
          "yang bisa jebol.")

    if total > BATAS_BYTE:
        print(f"\n! Kelebihan {mb(-sisa):.0f} MB dari jatah gratis. "
              f"Kelebihannya ditagih $0,015/GB per bulan — kecil, tapi "
              f"sebaiknya disadari.")
    elif bagian >= AMBANG_WASPADA:
        print(f"\n! Sudah {bagian*100:.0f}% dari jatah gratis. Yang paling boros:")
        for f in sorted(berkas, key=os.path.getsize, reverse=True)[:3]:
            print(f"    {mb(os.path.getsize(f)):6.0f} MB  {f}")

    setelan = baca_env()
    kurang = [k for k, v in setelan.items() if not v]
    if kurang:
        print(f"\n! Belum lengkap di .env.local: {', '.join(kurang)}")
        print("  Ambil dari Cloudflare: R2 -> Manage API Tokens -> Create")
        print("  (izin 'Object Read & Write', dibatasi ke bucket ini saja)")
        if not dry:
            return 1
        print("  --dry tetap dilanjutkan, tapi tanpa mengecek apa yang sudah ada di R2.")

    print()
    naik = lewat = gagal = 0
    for f in berkas:
        lokal = os.path.getsize(f)
        jauh = None if kurang else ukuran_di_r2(setelan, f)

        if jauh == lokal:
            print(f"  lewat   {f:<44} {mb(lokal):.0f} MB sudah ada")
            lewat += 1
            continue

        if dry:
            print(f"  unggah  {f:<44} {mb(lokal):.0f} MB")
            naik += 1
            continue

        print(f"  unggah  {f:<44} {mb(lokal):.0f} MB ... ", end='', flush=True)
        galat = unggah(setelan, f)
        if galat:
            print("GAGAL")
            print(f"          {galat}")
            gagal += 1
        else:
            print("selesai")
            naik += 1

    print(f"\nTerunggah: {naik}   Dilewati: {lewat}   Gagal: {gagal}")
    if not dry and not gagal:
        print(f"\nCek salah satunya di browser:\n  {BASE_VIDEO}/{berkas[0]}")
    return 1 if gagal else 0


if __name__ == '__main__':
    sys.exit(main())
