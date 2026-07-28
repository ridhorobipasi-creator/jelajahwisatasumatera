"""
Siapkan aset satu paket: rename + konversi + kompres.

Cara pakai:
    1. Taruh semua file mentah (foto & video) ke folder  assets/<paket>/_masuk/
       Nama file bebas — urutan mengikuti urutan nama file (natural sort).
       Khusus video, beri kata "hotel" atau "drone" di nama filenya.
    2. Jalankan:  python prepare_assets.py 4d3n
       Tambah --dry untuk melihat rencananya saja tanpa mengubah apa pun.

Hasilnya di assets/<paket>/ :
    frame-01.webp, frame-02.webp, ...      (dari file gambar)
    hotel-day1-web.mp4, hotel-day2-web.mp4 (dari video ber-nama "hotel")
    drone-1-web.mp4, drone-2-web.mp4, ...  (dari video ber-nama "drone")
    switzerland-web.mp4                    (dari video ber-nama "switzerland")
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

# Halaman ini lebarnya maksimal 480px, jadi aset tidak perlu resolusi penuh.
# Angka di bawah dipilih supaya file jauh lebih ringan tapi masih tajam di layar HP.
WEBP_QUALITY = 68
LEBAR_GAMBAR = 800    # foto di-resize ke lebar ini (1,7x lebar tampil)
CRF = 34              # makin besar makin kecil ukurannya (23 = bagus, 34 = seringan mungkin)
LEBAR_MAKS = 480      # video di-resize ke lebar maks ini (kartu video cuma ~200-360px)
FPS_MAKS = 30         # sumber banyak yang 60fps — dipotong separuh, hemat besar
PRESET = 'veryslow'   # encode lebih lama tapi file ~20% lebih kecil di kualitas sama
AUDIO_BITRATE = '56k' # mono 56k — cukup untuk musik latar di speaker HP


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


def olah_video(sumber, tujuan, dry):
    if dry:
        print(f"  [video ] {os.path.basename(sumber):<40} -> {os.path.basename(tujuan)}")
        return True
    cmd = [
        'ffmpeg', '-y', '-i', sumber,
        '-vf', f"scale='min({LEBAR_MAKS},iw)':-2,fps='min({FPS_MAKS},source_fps)'",
        '-vcodec', 'libx264', '-crf', str(CRF), '-preset', PRESET,
        '-profile:v', 'main', '-pix_fmt', 'yuv420p',
        '-movflags', '+faststart',          # penting: video bisa diputar sebelum selesai diunduh
        '-acodec', 'aac', '-ac', '1', '-b:a', AUDIO_BITRATE,
        tujuan,
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        print(f"  [video ] {os.path.basename(sumber):<40} -> {os.path.basename(tujuan)} "
              f"({mb(sumber):.1f}MB -> {mb(tujuan):.1f}MB)")
        return True
    except FileNotFoundError:
        print("  ! ffmpeg tidak ditemukan di PATH.")
        return False
    except subprocess.CalledProcessError as e:
        print(f"  ! Gagal kompres {os.path.basename(sumber)}: {e.stderr.decode(errors='ignore')[-300:]}")
        return False


def siapkan(paket, dry=False):
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

    gambar, hotel, drone, swiss, lain = [], [], [], [], []
    for f in berkas:
        ext = os.path.splitext(f)[1].lower()
        if ext in GAMBAR_EXT:
            gambar.append(f)
        elif ext in VIDEO_EXT:
            nama = f.lower()
            if 'hotel' in nama:
                hotel.append(f)
            elif 'drone' in nama:
                drone.append(f)
            elif 'switzerland' in nama:
                swiss.append(f)
            else:
                lain.append(f)
        else:
            lain.append(f)

    print(f"\n=== PAKET {paket.upper()} {'(DRY RUN — tidak ada yang diubah)' if dry else ''} ===")
    print(f"Ditemukan: {len(gambar)} gambar, {len(hotel)} video hotel, "
          f"{len(drone)} video drone, {len(swiss)} video switzerland")
    if lain:
        print(f"Dilewati (tidak dikenali): {', '.join(lain)}")
        print("  -> beri kata 'hotel', 'drone', atau 'switzerland' pada nama file video agar terbaca.")
    print()

    os.makedirs(folder, exist_ok=True)
    berhasil = 0

    for i, f in enumerate(gambar, start=1):
        tujuan = os.path.join(folder, f"frame-{i:02d}.webp")
        if olah_gambar(os.path.join(inbox, f), tujuan, dry):
            berhasil += 1

    for i, f in enumerate(hotel, start=1):
        tujuan = os.path.join(folder, f"hotel-day{i}-web.mp4")
        if olah_video(os.path.join(inbox, f), tujuan, dry):
            berhasil += 1

    for i, f in enumerate(drone, start=1):
        tujuan = os.path.join(folder, f"drone-{i}-web.mp4")
        if olah_video(os.path.join(inbox, f), tujuan, dry):
            berhasil += 1

    for f in swiss[:1]:
        tujuan = os.path.join(folder, "switzerland-web.mp4")
        if olah_video(os.path.join(inbox, f), tujuan, dry):
            berhasil += 1

    print(f"\nSelesai. {berhasil} file siap di {folder}/")
    if not dry:
        print(f"File mentah tetap ada di {inbox}/ (folder itu di-ignore git, aman).")
        print(f"Langkah berikutnya:  python build_trip.py {paket}")


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('-')]
    dry = '--dry' in sys.argv
    if not args:
        print(__doc__)
        print("Contoh:  python prepare_assets.py 4d3n")
        sys.exit(1)
    for paket in args:
        siapkan(paket, dry=dry)
