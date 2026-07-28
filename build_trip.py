"""
Generator halaman paket trip — semua paket memakai pola 5D4N
(deretan foto full-width + blok video hotel & drone diselipkan di tengah).

Cara pakai:
    python build_trip.py 4d3n            # bangun trip-4d3n.html
    python build_trip.py 2d1n 3d2n       # beberapa sekaligus
    python build_trip.py semua           # semua paket di PAKET
    python build_trip.py 4d3n --out preview/   # tulis ke folder lain (uji coba)

Sumber foto/video diambil otomatis dari assets/<paket>/ :
    frame-01.webp, frame-02.webp, ...   -> foto halaman, urut nomor
    hotel-day1-web.mp4, ...             -> video hotel (1 per malam)
    drone-1-web.mp4 ... drone-5-web.mp4 -> video drone
    switzerland-web.mp4                 -> video "Switzerland Danau Toba"

Urutan halaman mengikuti deck aslinya:
    foto 1-3  ->  blok video hotel  ->  blok video drone
              ->  blok video switzerland (4d3n & 5d4n)  ->  sisa foto

Atur isi teks tiap paket di bagian PAKET di bawah.
"""

import os
import re
import subprocess
import sys

WA = "6285272388532"

# Video tidak ikut ke GitHub (file mentah jauh di atas batas 100 MB per berkas),
# melainkan disimpan di Vercel Blob. Kosongkan jadi "" kalau suatu saat video
# dikembalikan ke dalam repo — sisa kodenya tidak perlu diubah.
BASE_VIDEO = "https://gv9h2lmr3uf0fwll.public.blob.vercel-storage.com"

# Label 5 video drone (sama untuk semua paket, ubah di sini kalau perlu)
LABEL_DRONE = [
    "CONTOH HASIL VIDEO<br>DRONE DJI MAVIC 4 PRO",
    "CONTOH HASIL VIDEO<br>IPHONE 17 PRO + DJI MAVIC 4 PRO",
    "CONTOH HASIL VIDEO<br>IPHONE 17 PRO + DJI MINI 3 & MAVIC 4 PRO",
    "CONTOH HASIL VIDEO<br>DRONE FPV DJI AVATA 360",
    "CONTOH HASIL VIDEO<br>IPHONE 17 PRO + DRONE DJI MINI 3",
]

TEKS_HOTEL_BAWAH = "KALAU MAU BOOK HOTEL SENDIRI JUGA BOLEH YA"

TEKS_SWISS = (
    "VIDEO DIBAWAH INI SALAH SATU ALASAN AWAK HARUS MEMILIH KAMI, KARENA KAMI AKAN "
    "MEMBAWA AWAK KE TEMPAT YANG DISEBUT SWITZERLAND DANAU TOBA.<br>"
    "DISAAT TOUR GUIDE LAIN TAK NAK BAWA TAMU KE TEMPAT NI SEBAB JAUH DAN JALAN SEMPIT, "
    "TAPI KAMI BERPRINSIP SEMUA ORANG KENA TENGOK TEMPAT CANTIK NI!!"
)

# ══════════════════════════════════════════════════════════════════════
#  KONFIGURASI TIAP PAKET
#  - video_hotel  : jumlah kartu video hotel (biasanya = jumlah malam)
#  - foto_atas    : berapa foto yang tampil SEBELUM blok video
#                   (sisanya otomatis tampil setelah blok video)
#  - hotel        : nama hotel per malam; "" kalau belum ada
#  - label_hotel  : ganti total label kartu hotel (default "HOTEL DAY n")
#  - judul_hotel  : ganti judul blok video hotel
#  - drone_dari   : folder sumber video drone (dipakai bersama antar paket)
#  - switzerland  : folder sumber switzerland-web.mp4; None = blok tidak dipakai
# ══════════════════════════════════════════════════════════════════════
PAKET = {
    "2d1n": {
        "video_hotel": 2,          # 1 malam, tamu boleh pilih salah satu dari 2 hotel
        "foto_atas": 3,
        "judul": "Explore Danau Toba 2D1N — Jelajahwisatasumatera",
        "deskripsi": "Paket Private Trip 2 Hari 1 Malam ke Danau Toba bersama Jelajah Wisata Sumatera. Pengalaman eksklusif dengan dokumentasi drone profesional.",
        "og_judul": "Explore Danau Toba 2D1N — Jelajah Wisata Sumatera",
        "og_deskripsi": "Paket liburan premium 2 Hari 1 Malam ke Danau Toba. Harga terbaik sudah termasuk dokumentasi lengkap!",
        "wa_teks": "Halo, saya tertarik dengan Paket Trip 2D1N Danau Toba",
        "judul_hotel": "(VIDEO HOTEL YANG AKAN DIGUNAKAN)<br>(BOLEH PILIH SALAH SATU HOTEL YA)",
        "label_hotel": ["OPSI PERTAMA<br>SAMOSIR COTTAGES", "OPSI KEDUA<br>HOPE VILLA"],
        "hotel": [],
        "drone_dari": "5d4n",
        "switzerland": None,
        "robots": "index, follow",
    },
    "3d2n": {
        "video_hotel": 2,
        "foto_atas": 3,
        "judul": "Explore Danau Toba 3D2N — Jelajahwisatasumatera",
        "deskripsi": "Paket Private Trip 3 Hari 2 Malam ke Danau Toba bersama Jelajah Wisata Sumatera. Pengalaman eksklusif dengan dokumentasi drone profesional.",
        "og_judul": "Explore Danau Toba 3D2N — Jelajah Wisata Sumatera",
        "og_deskripsi": "Paket liburan premium 3 Hari 2 Malam ke Danau Toba. Harga terbaik sudah termasuk dokumentasi lengkap!",
        "wa_teks": "Halo, saya tertarik dengan Paket Trip 3D2N Danau Toba",
        "hotel": ["Samosir Cottages", "Hope Villa"],
        "drone_dari": "5d4n",
        "switzerland": None,
        "robots": "index, follow",
    },
    "4d3n": {
        "video_hotel": 3,
        "foto_atas": 3,
        "judul": "Explore Danau Toba 4D3N — Jelajahwisatasumatera",
        "deskripsi": "Paket Private Trip 4 Hari 3 Malam ke Danau Toba bersama Jelajah Wisata Sumatera. Pengalaman eksklusif dengan dokumentasi drone profesional.",
        "og_judul": "Explore Danau Toba 4D3N — Jelajah Wisata Sumatera",
        "og_deskripsi": "Paket liburan premium 4 Hari 3 Malam ke Danau Toba. Harga terbaik sudah termasuk dokumentasi lengkap!",
        "wa_teks": "Halo, saya tertarik dengan Paket Trip 4D3N Danau Toba",
        "hotel": ["Ello Hotel", "Hope Villa", "Samosir Cottages"],
        "drone_dari": "5d4n",
        "switzerland": "5d4n",
        "robots": "index, follow",
    },
    "5d4n": {
        "video_hotel": 4,
        "foto_atas": 3,
        "judul": "Explore Danau Toba 5D4N — Jelajahwisatasumatera",
        "deskripsi": "Paket Private Trip 5 Hari 4 Malam ke Danau Toba bersama Jelajah Wisata Sumatera. Pengalaman eksklusif dengan dokumentasi drone profesional.",
        "og_judul": "Explore Danau Toba 5D4N — Jelajah Wisata Sumatera",
        "og_deskripsi": "Paket liburan premium 5 Hari 4 Malam ke Danau Toba. Harga terbaik sudah termasuk dokumentasi lengkap!",
        "wa_teks": "Halo, saya tertarik dengan Paket Trip 5D4N Danau Toba",
        "hotel": ["Ello Hotel", "Hope Villa", "Camping Holbung", "Samosir Cottages"],
        "drone_dari": "5d4n",
        "switzerland": "5d4n",
        "robots": "index, follow",
    },
}

SVG_WA = '<svg viewBox="0 0 24 24"><path d="M12 0C5.4 0 0 5.4 0 12c0 2.1.6 4.2 1.6 6L0 24l6.2-1.6c1.8 1 3.8 1.5 5.8 1.5 6.6 0 12-5.4 12-12S18.6 0 12 0zm0 21.8c-1.8 0-3.6-.5-5.1-1.4l-.4-.2-3.7 1 1-3.6-.2-.4c-1-1.6-1.5-3.4-1.5-5.2 0-5.5 4.5-9.9 9.9-9.9 5.5 0 9.9 4.5 9.9 9.9s-4.4 9.8-9.9 9.8zm5.5-7.4c-.3-.2-1.8-.9-2-1-.3-.1-.5-.2-.7.2-.2.3-.8 1-.9 1.1-.2.2-.3.2-.6.1-.3-.2-1.3-.5-2.4-1.5-.9-.8-1.5-1.8-1.7-2.1-.2-.3 0-.5.1-.6l.5-.5c.1-.2.2-.3.3-.5.1-.2 0-.4 0-.5 0-.2-.7-1.7-1-2.3-.2-.6-.5-.5-.7-.5h-.6c-.2 0-.5.1-.8.4-.3.3-1 1-1 2.5s1.1 2.9 1.2 3.1c.2.2 2.1 3.2 5.1 4.5.7.3 1.3.5 1.7.6.7.2 1.4.2 1.9.1.6-.1 1.8-.7 2-1.4.3-.7.3-1.3.2-1.4-.1-.2-.3-.3-.6-.4z"></path></svg>'

CSS = """        * { box-sizing: border-box; margin: 0; padding: 0; }

        html {
            /* Gambar latar estetik untuk tampilan Desktop */
            background: linear-gradient(rgba(0, 0, 0, 0.75), rgba(0, 0, 0, 0.75)), url('assets/danau-toba.png') no-repeat center center fixed;
            background-size: cover;
        }

        body {
            background: #000;
            line-height: 0;
            max-width: 480px;
            margin: 0 auto;
            position: relative;
            box-shadow: 0 0 50px rgba(0,0,0,0.8);
            min-height: 100vh;
            -webkit-overflow-scrolling: touch;
            touch-action: pan-y;
            overscroll-behavior-y: contain;
        }

        /* ── Back Button ── */
        .back-btn {
            position: absolute;
            top: 24px;
            left: 20px;
            width: 44px;
            height: 44px;
            border-radius: 50%;
            background: rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            display: flex;
            align-items: center;
            justify-content: center;
            border: 1px solid rgba(255, 255, 255, 0.15);
            text-decoration: none;
            z-index: 100;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            transition: all 0.3s ease;
        }
        .back-btn:hover {
            background: rgba(255, 255, 255, 0.15);
            transform: scale(1.05);
        }
        .back-btn svg { width: 22px; height: 22px; stroke: #fff; stroke-width: 2.5; stroke-linecap: round; stroke-linejoin: round; fill: none; }

        /* ── Frame gambar biasa ── */
        .frame {
            /* Render off-screen frames hanya saat mau masuk viewport */
            content-visibility: auto;
            contain-intrinsic-size: 0 600px;
        }
        .frame img {
            width: 100%;
            display: block;
        }

        /* ── Fade-in video saat mulai play ── */
        video {
            opacity: 0;
            transition: opacity 0.35s ease;
        }
        video.is-playing {
            opacity: 1;
        }

        /* ── Blok video (hotel & drone) ── */
        .custom-frame {
            width: 100%;
            max-width: 480px;
            margin: 0 auto;
            background: radial-gradient(circle at top right, #0d2611, #040a05);
            padding: 40px 15px;
            font-family: 'Arial', sans-serif;
            color: #fff;
            position: relative;
            line-height: 1.4;
        }

        .drone-screen-2 {
            background: radial-gradient(circle at bottom left, #0d2611, #040a05);
            padding-top: 20px;
            padding-bottom: 60px;
        }

        .drone-title {
            text-align: center;
            font-size: 18px;
            font-weight: 900;
            color: #fff;
            margin-bottom: 24px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.5);
            letter-spacing: 0.5px;
            line-height: 1.3;
        }

        .drone-grid-2 {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-bottom: 16px;
        }

        .drone-grid-1 {
            display: grid;
            grid-template-columns: 1fr;
            padding: 0 15%;
            margin-bottom: 24px;
        }

        /* Video tunggal yang tampil lebih lebar (Switzerland Danau Toba) */
        .solo-grid {
            display: grid;
            grid-template-columns: 1fr;
            padding: 0 8%;
        }

        /* Catatan kecil di bawah blok video */
        .frame-note {
            text-align: center;
            font-size: 13px;
            font-weight: 800;
            color: #d8f5d6;
            margin-top: 20px;
            letter-spacing: 0.3px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.5);
        }

        .swiss-intro {
            font-size: 12.5px;
            font-weight: 700;
            color: #e0f2e3;
            text-align: center;
            line-height: 1.5;
            margin-bottom: 22px;
            padding: 0 10px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.5);
        }

        .vid-card {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 8px;
            text-align: center;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }

        .vid-card .vid-label {
            font-size: 10.5px;
            font-weight: 700;
            margin-bottom: 8px;
            color: #e0f2e3;
            text-transform: uppercase;
            min-height: 28px;
            display: flex;
            align-items: center;
            justify-content: center;
            line-height: 1.2;
        }

        .vid-card video {
            width: 100%;
            aspect-ratio: 9 / 16;
            object-fit: cover;
            border-radius: 8px;
            background: #111;
            display: block;
        }

        .drone-alert {
            text-align: center;
            margin-top: 32px;
            padding: 0 10px;
        }

        .drone-logo {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            margin-bottom: 12px;
            border: 2px solid #25D366;
            background: #fff;
            padding: 2px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }

        .drone-alert p {
            font-size: 13.5px;
            font-weight: 800;
            color: #d8f5d6;
            line-height: 1.5;
            text-shadow: 0 2px 4px rgba(0,0,0,0.5);
            letter-spacing: 0.3px;
        }

        /* ── Floating WhatsApp ── */
        .floating-wa {
            position: fixed;
            right: 20px;
            bottom: 20px;
            width: 54px;
            height: 54px;
            border-radius: 50%;
            background: #25D366;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 6px 24px rgba(0, 0, 0, 0.5);
            z-index: 9999;
            text-decoration: none;
        }
        .floating-wa svg { width: 28px; height: 28px; fill: #fff; }"""

SCRIPT = """    <!-- ── Video Controller Script ── -->
    <script>
        document.addEventListener('DOMContentLoaded', () => {
            const videos = document.querySelectorAll('video');

            videos.forEach(video => {
                video.style.opacity = '1';

                // Saat satu video diputar, video lain otomatis berhenti
                video.addEventListener('play', () => {
                    videos.forEach(v => {
                        if (v !== video && !v.paused) v.pause();
                    });
                });
            });
        });
    </script>"""


def cari_frame(folder):
    """Ambil semua frame-NN.webp di folder, urut nomor."""
    if not os.path.isdir(folder):
        return []
    hasil = []
    for f in os.listdir(folder):
        m = re.fullmatch(r'frame-(\d+)\.webp', f)
        if m:
            hasil.append((int(m.group(1)), f))
    return [f for _, f in sorted(hasil)]


def blok_foto(paket, berkas, judul_komentar, prioritas_pertama=False):
    if not berkas:
        return ""
    out = f"""
    <!-- ═══════════════════════════════════════════ -->
    <!-- {judul_komentar:<42} -->
    <!-- ═══════════════════════════════════════════ -->
"""
    for i, f in enumerate(berkas):
        if prioritas_pertama and i == 0:
            atribut = 'fetchpriority="high" decoding="async"'
        else:
            atribut = 'decoding="async" loading="lazy"'
        nomor = re.search(r'\d+', f).group()
        out += f"""    <div class="frame">
        <img src="assets/{paket}/{f}" alt="{paket.upper()} halaman {nomor}" {atribut}>
    </div>
"""
    return out


def tipe_video(path_lokal):
    """Atribut type untuk <source>, lengkap dengan nama codec-nya.

    Nama codec ini yang membuat browser tahu ia sanggup atau tidak SEBELUM
    mengunduh. Tanpa itu, browser yang tidak bisa HEVC tetap menarik file
    ratusan MB lalu menampilkan kotak hitam, bukan pindah ke cadangan.
    """
    try:
        hasil = subprocess.run(
            ['ffprobe', '-v', 'error', '-select_streams', 'v:0',
             '-show_entries', 'stream=codec_tag_string', '-of', 'csv=p=0', path_lokal],
            check=True, capture_output=True,
        )
        tag = hasil.stdout.decode(errors='ignore').strip()
    except Exception:
        tag = ''
    if tag == 'hvc1':
        return 'video/mp4; codecs=&quot;hvc1&quot;'
    if tag == 'avc1':
        return 'video/mp4; codecs=&quot;avc1.640028&quot;'
    return 'video/mp4'


def sumber_video(nama):
    """Dua baris <source> untuk satu video: kualitas asli dulu, lalu cadangan.

    `nama` berupa 'assets/5d4n/hotel-day1' — tanpa akhiran. Berkas -asli.mp4
    berisi gambar & suara persis seperti yang diberikan (tanpa encode ulang);
    -web.mp4 adalah versi H.264 untuk browser yang tidak mendukung HEVC.
    """
    baris = []
    for akhiran in ('-asli', '-web'):
        lokal = f"{nama}{akhiran}.mp4"
        if not os.path.exists(lokal):
            continue
        url = f"{BASE_VIDEO}/{lokal}" if BASE_VIDEO else lokal
        baris.append(f'                    <source src="{url}#t=0.001" '
                     f'type="{tipe_video(lokal)}">')
    return '\n'.join(baris)


def kartu_video(label, nama):
    return f"""            <div class="vid-card">
                <div class="vid-label">{label}</div>
                <video controls loop muted playsinline preload="metadata">
{sumber_video(nama)}
                </video>
            </div>
"""


def blok_hotel(paket, cfg):
    jumlah = cfg["video_hotel"]
    nama = list(cfg.get("hotel") or [])
    nama += [""] * (jumlah - len(nama))

    label_khusus = cfg.get("label_hotel") or []
    judul = cfg.get("judul_hotel") or "(VIDEO HOTEL YANG AKAN DIGUNAKAN)"

    out = f"""
    <!-- ═══════════════════════════════════════════ -->
    <!-- BLOK VIDEO HOTEL                           -->
    <!-- ═══════════════════════════════════════════ -->
    <div class="custom-frame drone-screen-1">
        <h2 class="drone-title">{judul}</h2>
"""
    for i in range(0, jumlah, 2):
        # Baris terakhir yang cuma berisi 1 video dibuat 1 kolom agar tetap di tengah
        sisa = min(2, jumlah - i)
        grid = "drone-grid-2" if sisa == 2 else "drone-grid-1"
        out += f'\n        <div class="{grid}">\n'
        for j in range(sisa):
            n = i + j
            if n < len(label_khusus):
                label = label_khusus[n]
            else:
                label = f"HOTEL DAY {n + 1}"
                if nama[n]:
                    label += f"<br>{nama[n]}"
            out += kartu_video(label, f"assets/{paket}/hotel-day{n + 1}")
        out += '        </div>\n'
    out += f'\n        <p class="frame-note">{TEKS_HOTEL_BAWAH}</p>\n'
    out += '    </div>\n'
    return out


def blok_switzerland(cfg):
    sumber = cfg.get("switzerland")
    if not sumber:
        return ""
    return f"""
    <!-- ══════════════════════════════════════════════════════════════ -->
    <!-- BLOK VIDEO SWITZERLAND DANAU TOBA                              -->
    <!-- ══════════════════════════════════════════════════════════════ -->
    <div class="custom-frame drone-screen-1">
        <p class="swiss-intro">{TEKS_SWISS}</p>

        <div class="solo-grid">
            <div class="vid-card">
                <video controls loop muted playsinline preload="metadata">
{sumber_video(f"assets/{sumber}/switzerland")}
                </video>
            </div>
        </div>
    </div>
"""


def blok_drone(cfg):
    sumber = cfg.get("drone_dari") or cfg["_paket"]
    label = cfg.get("label_drone") or LABEL_DRONE

    def src(n):
        return f"assets/{sumber}/drone-{n}"

    out = """
    <!-- ══════════════════════════════════════════════════════════════ -->
    <!-- BLOK VIDEO DRONE (Layar 1)                                     -->
    <!-- ══════════════════════════════════════════════════════════════ -->
    <div class="custom-frame drone-screen-1">
        <h2 class="drone-title">(HASIL VIDEO DRONE + EDITING)</h2>

        <div class="drone-grid-2">
"""
    out += kartu_video(label[0], src(1))
    out += kartu_video(label[1], src(2))
    out += """        </div>

        <div class="drone-grid-1">
"""
    out += kartu_video(label[2], src(3))
    out += """        </div>
    </div>

    <!-- ══════════════════════════════════════════════════════════════ -->
    <!-- BLOK VIDEO DRONE (Layar 2)                                     -->
    <!-- ══════════════════════════════════════════════════════════════ -->
    <div class="custom-frame drone-screen-2">
        <div class="drone-grid-2">
"""
    out += kartu_video(label[3], src(4))
    out += kartu_video(label[4], src(5))
    out += """        </div>

        <div class="drone-alert">
            <img src="assets/avatar.jpg" alt="Logo Jelajahwisatasumatera" class="drone-logo">
            <p>SEMUA VIDEO DIATAS ASLI DARI GEAR CAMERA DAN DRONE KAMI,<br>BUKAN AMBIL VIDEO ORANG LAIN!!</p>
        </div>
    </div>
"""
    return out


def bangun(paket, cfg, folder_keluar='.'):
    cfg = dict(cfg, _paket=paket)
    folder_aset = os.path.join('assets', paket)
    frames = cari_frame(folder_aset)
    atas = frames[: cfg["foto_atas"]]
    bawah = frames[cfg["foto_atas"]:]

    wa_link = f"https://wa.me/{WA}?text={cfg['wa_teks'].replace(' ', '%20').replace(',', '%2C')}"

    html = f"""<!DOCTYPE html>
<html lang="id">

<head>
    <link rel="icon" type="image/png" sizes="32x32" href="assets/favicon-32.png">
    <link rel="icon" type="image/png" sizes="64x64" href="assets/favicon-64.png">
    <link rel="icon" type="image/png" sizes="512x512" href="assets/favicon-512.png">
    <link rel="apple-touch-icon" sizes="180x180" href="assets/apple-touch-icon.png">
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="robots" content="{cfg['robots']}" />
    <title>{cfg['judul']}</title>

    <!-- Meta SEO & OpenGraph -->
    <meta name="description" content="{cfg['deskripsi']}" />
    <meta property="og:title" content="{cfg['og_judul']}" />
    <meta property="og:description" content="{cfg['og_deskripsi']}" />
    <meta property="og:image" content="assets/danau-toba.png" />
    <meta property="og:type" content="website" />

    <style>
{CSS}
    </style>
</head>

<body>

    <!-- ── Back Button ── -->
    <a href="/" class="back-btn" title="Kembali ke Beranda">
        <svg viewBox="0 0 24 24"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
    </a>
{blok_foto(paket, atas, 'FOTO BAGIAN ATAS', prioritas_pertama=True)}{blok_hotel(paket, cfg)}{blok_drone(cfg)}{blok_switzerland(cfg)}{blok_foto(paket, bawah, 'FOTO BAGIAN BAWAH')}
    <!-- ── Floating WhatsApp ── -->
    <a href="{wa_link}" class="floating-wa" target="_blank" aria-label="Chat WhatsApp">
        {SVG_WA}
    </a>

{SCRIPT}
</body>

</html>
"""

    os.makedirs(folder_keluar, exist_ok=True)
    tujuan = os.path.join(folder_keluar, f"trip-{paket}.html")
    with open(tujuan, 'w', encoding='utf-8', newline='\n') as f:
        f.write(html)

    # Laporan + peringatan aset yang belum ada
    print(f"\n✓ {tujuan}")
    print(f"  foto : {len(frames)} ({len(atas)} di atas blok video, {len(bawah)} di bawah)")
    def cek(dasar, kumpulan):
        """Cukup salah satu dari -asli.mp4 / -web.mp4 yang ada."""
        if not any(os.path.exists(f"{dasar}{a}.mp4") for a in ('-asli', '-web')):
            kumpulan.append(f"{dasar}-*.mp4")

    hilang = []
    for n in range(1, cfg["video_hotel"] + 1):
        cek(os.path.join(folder_aset, f"hotel-day{n}"), hilang)
    sumber_drone = cfg.get("drone_dari") or paket
    for n in range(1, 6):
        cek(os.path.join('assets', sumber_drone, f"drone-{n}"), hilang)
    sumber_swiss = cfg.get("switzerland")
    if sumber_swiss:
        cek(os.path.join('assets', sumber_swiss, "switzerland"), hilang)
    print(f"  video: {cfg['video_hotel']} hotel + 5 drone (dari assets/{sumber_drone}/)"
          + (f" + switzerland (dari assets/{sumber_swiss}/)" if sumber_swiss else ""))
    if not frames:
        print(f"  ! belum ada frame-NN.webp di {folder_aset}/ — halaman masih tanpa foto")
    for p in hilang:
        print(f"  ! video belum ada: {p}")


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('-')]
    keluar = '.'
    if '--out' in sys.argv:
        i = sys.argv.index('--out')
        if i + 1 < len(sys.argv):
            keluar = sys.argv[i + 1]
            args = [a for a in args if a != keluar]

    if not args:
        print(__doc__)
        print("Paket tersedia:", ', '.join(PAKET))
        sys.exit(1)

    daftar = list(PAKET) if args[0] in ('semua', 'all') else args
    for paket in daftar:
        if paket not in PAKET:
            print(f"! Paket '{paket}' tidak ada di konfigurasi PAKET.")
            continue
        bangun(paket, PAKET[paket], keluar)
    print()
