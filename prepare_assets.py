"""
Siapkan aset: rename + konversi + kompres.

FOTO per paket, VIDEO di satu folder bersama
────────────────────────────────────────────
Foto beda-beda tiap paket, tapi video hotel banyak yang dipakai bersama —
Samosir Cottages misalnya muncul di keempat paket. Karena itu video tidak lagi
disalin per paket (dulu berkas yang sama tersimpan sampai 4 kali), melainkan
duduk di satu folder dan dipanggil bersama-sama.

FOTO
    1. Taruh foto ke  assets/<paket>/_masuk/
       Nama bebas — urutan tampil mengikuti urutan nama (natural sort).
    2. Jalankan:  python prepare_assets.py 4d3n
    -> assets/<paket>/frame-01.webp, frame-02.webp, ...

VIDEO
    1. Taruh video ke  assets/video/_masuk/
       Nama berkasnya JADI nama video di web, jadi beri nama menurut isinya:
           hotel-ello.mov  ->  assets/video/hotel-ello-web.mp4
           drone-1.mp4     ->  assets/video/drone-1-web.mp4
    2. Jalankan:  python prepare_assets.py video

Tambah --dry untuk melihat rencananya saja tanpa mengubah apa pun.

Setelah videonya jadi, daftarkan ke paket yang memakainya lewat "hotel_video"
di bagian PAKET pada build_trip.py.
"""

import os
import re
import sys
import shutil
import subprocess

try:
    from PIL import Image
except ImportError:
    Image = None

GAMBAR_EXT = {'.png', '.jpg', '.jpeg', '.webp', '.heic'}
VIDEO_EXT = {'.mp4', '.mov', '.m4v', '.avi'}

# Semua video dari semua paket duduk di sini — lihat catatan di atas.
FOLDER_VIDEO = os.path.join('assets', 'video')

# Halaman ini lebarnya maksimal 480px, jadi aset tidak perlu resolusi penuh.
# Angka di bawah dipilih supaya file jauh lebih ringan tapi masih tajam di layar HP.
WEBP_QUALITY = 88
LEBAR_GAMBAR = 1440    # foto di-resize ke lebar ini (3x lebar tampil)
CRF = 23               # 23 = masih tajam di layar; 20 dulu boros tanpa beda terlihat
LEBAR_MAKS = None      # None = resolusi video dibiarkan asli, tidak dikecilkan
PRESET = 'slow'        # encode lebih lama tapi file lebih kecil di kualitas sama
AUDIO_BITRATE = '192k' # stereo penuh

# Atap bitrate. Tanpa ini CRF bebas membengkak di adegan bergerak cepat — video
# drone switzerland dulu menembus 8,8 Mbps alias 304 MB untuk 5 menit, padahal
# jatah Vercel Blob paket Hobby cuma 1 GB untuk SELURUH video. Atap ini membuat
# satu berkas tidak bisa lagi diam-diam menghabiskan sepertiga kuota.
MAXRATE = '4M'
BUFSIZE = '8M'

# Kalau True, tiap video juga menghasilkan nama-asli.mp4 — aliran sumber disalin
# apa adanya tanpa encode ulang, kualitasnya identik dengan berkas yang diberikan.
#
# Dimatikan sejak 2026-07-28. Berkas itu hampir selalu HEVC (H.265): Safari bisa
# memutarnya, tapi Chrome di Windows perlu codec berbayar dan Firefox tidak
# mendukung sama sekali — jadi ia cuma melayani sebagian pengunjung sementara
# ukurannya dua kali lipat versi web. Bersama-sama totalnya menembus batas 1 GB
# Vercel Blob paket Hobby dan unggahan berhenti di tengah. Halaman sekarang
# memakai satu berkas H.264 per video yang jalan di semua browser.
#
# Nyalakan lagi kalau pindah ke paket berbayar — build_trip.py tinggal
# dikembalikan '-asli' ke AKHIRAN_VIDEO.
SALIN_ASLI = False


def urut_natural(nama):
    """Urutkan 'foto2' sebelum 'foto10'."""
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)', nama)]


def mb(path):
    return os.path.getsize(path) / (1024 * 1024)


def olah_gambar(sumber, tujuan, dry):
    if dry:
        print(f"  [gambar] {os.path.basename(sumber):<40} -> {os.path.basename(tujuan)}")
        return True
    if Image is None:
        print("  ! Pillow belum terpasang. Jalankan: pip install Pillow")
        return False
    try:
        with Image.open(sumber) as img:
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGBA')
            else:
                img = img.convert('RGB')
            if img.width > LEBAR_GAMBAR:
                tinggi = round(img.height * LEBAR_GAMBAR / img.width)
                img = img.resize((LEBAR_GAMBAR, tinggi), Image.LANCZOS)
            img.save(tujuan, 'WEBP', quality=WEBP_QUALITY, method=6)
        print(f"  [gambar] {os.path.basename(sumber):<40} -> {os.path.basename(tujuan)} "
              f"({mb(sumber):.1f}MB -> {mb(tujuan):.1f}MB)")
        return True
    except Exception as e:
        print(f"  ! Gagal konversi {os.path.basename(sumber)}: {e}")
        return False


def codec_video(path):
    """Nama codec video di sebuah file, mis. 'h264'. Kosong kalau gagal dibaca."""
    try:
        hasil = subprocess.run(
            ['ffprobe', '-v', 'error', '-select_streams', 'v:0',
             '-show_entries', 'stream=codec_name', '-of', 'csv=p=0', path],
            check=True, capture_output=True,
        )
        return hasil.stdout.decode(errors='ignore').strip()
    except Exception:
        return ''


def salin_asli(sumber, tujuan):
    """Pindahkan sumber ke wadah .mp4 tanpa menyentuh gambar & suaranya.

    Tidak ada encode ulang di sini — aliran datanya disalin utuh, jadi hasilnya
    identik dengan file yang diberikan. Tag 'hvc1' wajib supaya Safari mengenali
    aliran HEVC-nya; tanpa itu Safari diam saja meski sebenarnya sanggup.
    """
    cmd = ['ffmpeg', '-y', '-i', sumber, '-c', 'copy',
           '-movflags', '+faststart', tujuan]
    if codec_video(sumber) == 'hevc':
        cmd[-1:-1] = ['-tag:v', 'hvc1']
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        print(f"  [asli  ] {os.path.basename(sumber):<40} -> {os.path.basename(tujuan)} "
              f"({mb(tujuan):.1f}MB, disalin tanpa encode ulang)")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ! Gagal menyalin {os.path.basename(sumber)}: "
              f"{e.stderr.decode(errors='ignore')[-300:]}")
        return False


def olah_video(sumber, tujuan, dry, hanya_asli=False):
    if dry:
        print(f"  [video ] {os.path.basename(sumber):<40} -> {os.path.basename(tujuan)}")
        return True
    if hanya_asli:
        # Versi H.264-nya sudah ada dari jalan sebelumnya — cukup buat salinan aslinya.
        return salin_asli(sumber, tujuan.replace('-web.mp4', '-asli.mp4'))
    cmd = ['ffmpeg', '-y', '-i', sumber]
    if LEBAR_MAKS:
        cmd += ['-vf', f"scale='min({LEBAR_MAKS},iw)':-2"]
    cmd += [
        '-vcodec', 'libx264', '-crf', str(CRF), '-preset', PRESET,
        '-maxrate', MAXRATE, '-bufsize', BUFSIZE,      # atap bitrate, lihat catatan di atas
        '-profile:v', 'high', '-pix_fmt', 'yuv420p',   # 'high' lebih efisien di 1080p
        '-movflags', '+faststart',          # penting: video bisa diputar sebelum selesai diunduh
        '-acodec', 'aac', '-b:a', AUDIO_BITRATE,
        tujuan,
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        catatan = ''
        # Kalau sumbernya sudah H.264 dan kecil, encode ulang justru membengkakkan
        # file tanpa menambah kualitas. Dalam kasus itu pakai sumbernya langsung,
        # cuma dikemas ulang — hasilnya lebih kecil DAN gambarnya persis asli.
        if mb(tujuan) > mb(sumber) and codec_video(sumber) == 'h264':
            remux = ['ffmpeg', '-y', '-i', sumber, '-c', 'copy',
                     '-movflags', '+faststart', tujuan]
            subprocess.run(remux, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            catatan = '  [pakai sumber apa adanya, tanpa encode ulang]'
        print(f"  [video ] {os.path.basename(sumber):<40} -> {os.path.basename(tujuan)} "
              f"({mb(sumber):.1f}MB -> {mb(tujuan):.1f}MB){catatan}")
        if SALIN_ASLI:
            salin_asli(sumber, tujuan.replace('-web.mp4', '-asli.mp4'))
        return True
    except FileNotFoundError:
        print("  ! ffmpeg tidak ditemukan di PATH.")
        return False
    except subprocess.CalledProcessError as e:
        print(f"  ! Gagal kompres {os.path.basename(sumber)}: {e.stderr.decode(errors='ignore')[-300:]}")
        return False


def siapkan(paket, dry=False, hanya_asli=False):
    folder = os.path.join('assets', paket)
    inbox = os.path.join(folder, '_masuk')

    if not os.path.isdir(inbox):
        os.makedirs(inbox, exist_ok=True)
        print(f"Folder {inbox} dibuat. Taruh foto & video mentah di situ, lalu jalankan lagi.")
        return

    berkas = sorted(
        (f for f in os.listdir(inbox) if os.path.isfile(os.path.join(inbox, f))),
        key=urut_natural,
    )
    if not berkas:
        print(f"Tidak ada file di {inbox}.")
        return

    gambar, video, lain = [], [], []
    for f in berkas:
        ext = os.path.splitext(f)[1].lower()
        if ext in GAMBAR_EXT:
            gambar.append(f)
        elif ext in VIDEO_EXT:
            video.append(f)
        else:
            lain.append(f)

    print(f"\n=== PAKET {paket.upper()} {'(DRY RUN — tidak ada yang diubah)' if dry else ''} ===")
    print(f"Ditemukan: {len(gambar)} gambar")
    if video:
        # Video di sini tidak lagi diproses: satu video sering dipakai beberapa
        # paket, jadi tempatnya di folder bersama.
        print(f"Dilewati ({len(video)} video): {', '.join(video)}")
        print(f"  -> video sekarang diproses terpisah. Pindahkan ke "
              f"{os.path.join(FOLDER_VIDEO, '_masuk')}/ lalu jalankan:")
        print("     python prepare_assets.py video")
    if lain:
        print(f"Dilewati (bukan gambar): {', '.join(lain)}")
    print()

    os.makedirs(folder, exist_ok=True)
    berhasil = 0

    if not hanya_asli:
        for i, f in enumerate(gambar, start=1):
            tujuan = os.path.join(folder, f"frame-{i:02d}.webp")
            if olah_gambar(os.path.join(inbox, f), tujuan, dry):
                berhasil += 1

    print(f"\nSelesai. {berhasil} foto siap di {folder}/")
    if not dry:
        print(f"File mentah tetap ada di {inbox}/ (folder itu di-ignore git, aman).")
        print(f"Langkah berikutnya:  python build_trip.py {paket}")


def nama_video(berkas):
    """Nama berkas mentah -> nama video di web.

    'HOTEL ELLO.mov' -> 'hotel-ello'. Nama inilah yang nanti disebut di
    "hotel_video" pada build_trip.py, jadi sengaja dibuat mudah ditebak.
    """
    dasar = os.path.splitext(berkas)[0].lower()
    return re.sub(r'[^a-z0-9]+', '-', dasar).strip('-')


def siapkan_video(dry=False, hanya_asli=False):
    """Kompres semua video di assets/video/_masuk/ ke assets/video/."""
    inbox = os.path.join(FOLDER_VIDEO, '_masuk')

    if not os.path.isdir(inbox):
        os.makedirs(inbox, exist_ok=True)
        print(f"Folder {inbox} dibuat. Taruh video mentah di situ, lalu jalankan lagi.")
        return

    berkas = sorted(
        (f for f in os.listdir(inbox)
         if os.path.isfile(os.path.join(inbox, f))
         and os.path.splitext(f)[1].lower() in VIDEO_EXT),
        key=urut_natural,
    )
    if not berkas:
        print(f"Tidak ada video di {inbox}.")
        return

    print(f"\n=== VIDEO {'(DRY RUN — tidak ada yang diubah)' if dry else ''} ===")
    print(f"Ditemukan {len(berkas)} video.\n")

    os.makedirs(FOLDER_VIDEO, exist_ok=True)
    berhasil = 0
    dipakai = {}
    for f in berkas:
        nama = nama_video(f)
        if nama in dipakai:
            print(f"  ! {f} dan {dipakai[nama]} menghasilkan nama sama "
                  f"('{nama}') — yang kedua dilewati.")
            continue
        dipakai[nama] = f
        tujuan = os.path.join(FOLDER_VIDEO, f"{nama}-web.mp4")
        if olah_video(os.path.join(inbox, f), tujuan, dry, hanya_asli):
            berhasil += 1

    print(f"\nSelesai. {berhasil} video siap di {FOLDER_VIDEO}/")
    if not dry:
        print(f"File mentah tetap ada di {inbox}/ (folder itu di-ignore git, aman).")
        print("Langkah berikutnya: daftarkan video hotel ke paketnya lewat "
              "\"hotel_video\" di build_trip.py,")
        print("lalu:  python build_trip.py semua")


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('-')]
    dry = '--dry' in sys.argv
    hanya_asli = '--hanya-asli' in sys.argv   # lewati foto & encode H.264 yang sudah jadi
    if not args:
        print(__doc__)
        print("Contoh:  python prepare_assets.py 4d3n     (foto paket 4D3N)")
        print("         python prepare_assets.py video    (semua video)")
        sys.exit(1)
    for paket in args:
        if paket == 'video':
            siapkan_video(dry=dry, hanya_asli=hanya_asli)
        else:
            siapkan(paket, dry=dry, hanya_asli=hanya_asli)
