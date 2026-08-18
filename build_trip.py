"""
Generator halaman paket trip — semua paket memakai pola 5D4N
(deretan foto full-width + blok video hotel & drone diselipkan di tengah).

Cara pakai:
    python build_trip.py 4d3n            # bangun trip-4d3n.html
    python build_trip.py 2d1n 3d2n       # beberapa sekaligus
    python build_trip.py semua           # semua paket di PAKET
    python build_trip.py 4d3n --out preview/   # tulis ke folder lain (uji coba)

Foto diambil per paket, video disemat dari YouTube:

    assets/<paket>/frame-01.webp, frame-02.webp, ...  -> foto halaman, urut nomor

    assets/video/hotel-*.mp4              -> video hotel, dinamai menurut hotelnya
    assets/video/drone-1..5-web.mp4       -> video drone, sama untuk semua paket
    assets/video/switzerland-web.mp4      -> video "Switzerland Danau Toba"

Berkas mp4 itu arsip lokal, bukan yang dilayani ke pengunjung: halaman menyemat
videonya dari YouTube lewat peta YOUTUBE di bawah, dan menampilkan sampul dari
assets/poster/ sampai pengunjung menekan play.

Video sengaja tidak dipisah per paket: hotel yang sama dipakai beberapa paket,
jadi satu berkas dipakai bersama-sama. Paket mana memakai video hotel yang mana
diatur lewat "hotel_video" di bagian PAKET.

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

# ── Video: disemat dari YouTube ────────────────────────────────────────
#
# Dulu video dilayani sendiri lewat Vercel Blob. Itu mati pada 2026-08-02:
# paket Hobby memberi 10 GB transfer sebulan dan situs ini memakai 21,4 GB
# dalam 5 hari, jadi seluruh store diblokir dan semua video di keempat halaman
# membalas 403 serentak. Satu halaman memanggil ratusan MB video — belasan
# pengunjung yang menonton lengkap sudah menghabiskan jatah sebulan, artinya
# situs yang laku justru yang paling cepat mati.
#
# YouTube tidak menagih transfer sama sekali, jadi masalah itu tidak bisa
# terulang berapa pun ramainya pengunjung.
#
# Isi peta di bawah dengan ID video YouTube-nya — potongan 11 huruf di alamat
# https://youtu.be/XXXXXXXXXXX atau .../watch?v=XXXXXXXXXXX. Kuncinya nama
# berkas di assets/video/ tanpa akhiran '-web'.
#
# Video harus "Unlisted" (tidak publik tapi bisa disemat) atau "Public".
# "Private" TIDAK bisa disemat — hasilnya kotak hitam di halaman.
YOUTUBE = {
    "hotel-samosir-cottages":  "",
    "hotel-hope-villa":        "",
    "hotel-hope-villa-2d1n":   "",
    "hotel-ello":              "",
    "hotel-camping-holbung":   "",
    "drone-1":                 "",
    "drone-2":                 "",
    "drone-3":                 "",
    "drone-4":                 "",
    "drone-5":                 "",
    "switzerland":             "",
}

# Gambar sampul kartu video, dibuat dari berkas video lokal:
#
#   ffmpeg -ss 1 -i assets/video/NAMA-web.mp4 -frames:v 1 \
#          -vf scale=540:-2 -q:v 72 assets/poster/NAMA.webp
#
# Sampul ini dipakai supaya iframe YouTube tidak dimuat sebelum diklik. Sebelas
# iframe sekaligus berarti sebelas player YouTube ikut diunduh saat halaman
# dibuka — berat sekali di HP. Dengan sampul, yang dimuat awalnya cuma gambar
# ±40 KB, dan player baru datang saat pengunjung benar-benar menekan play.
#
# Sampulnya ikut ke GitHub (kecil) dan dilayani Vercel, bukan YouTube — memakai
# thumbnail bawaan YouTube tidak dipilih karena video tegak 9:16 diberi bilah
# hitam kiri-kanan di sana.
FOLDER_POSTER = "assets/poster"

# SEMUA video duduk di satu folder ini, bukan dipisah per paket.
#
# Dulu tiap paket punya salinan videonya sendiri (assets/5d4n/hotel-day1-web.mp4,
# assets/4d3n/hotel-day1-web.mp4, ...). Karena beberapa hotel dipakai lebih dari
# satu paket, video yang sama tersimpan sampai 4 kali dengan alamat berbeda:
# 918 MB simpanan padahal isinya cuma 671 MB. Lebih buruk lagi di sisi transfer —
# pengunjung yang membandingkan beberapa paket mengunduh berkas yang sama
# berulang kali karena browser melihatnya sebagai alamat berbeda.
#
# Sekarang satu video = satu berkas = satu alamat, dinamai menurut isinya
# (nama hotel), bukan menurut hari ke berapa ia muncul di sebuah paket.
FOLDER_VIDEO = "assets/video"

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
#  - hotel_video  : nama berkas video hotel per malam, tanpa akhiran, dari
#                   assets/video/. Jumlah isinya = jumlah malam/kartu video.
#                   Paket yang menginap di hotel sama menyebut berkas yang sama —
#                   di situlah penghematannya.
#  - foto_atas    : berapa foto yang tampil SEBELUM blok video
#                   (sisanya otomatis tampil setelah blok video)
#  - hotel        : nama hotel per malam; "" kalau belum ada
#  - label_hotel  : ganti total label kartu hotel (default "HOTEL DAY n")
#  - judul_hotel  : ganti judul blok video hotel
#  - switzerland  : True kalau blok Switzerland Danau Toba ikut ditampilkan
#
#  Video drone sama untuk semua paket, jadi tidak perlu diatur di sini.
# ══════════════════════════════════════════════════════════════════════
PAKET = {
    "2d1n": {
        # 1 malam, tamu boleh pilih salah satu dari 2 hotel.
        # Hope Villa di sini editannya lain (72,6 detik) dari yang dipakai paket
        # lain (67,5 detik) — sengaja berkas terpisah, bukan duplikat.
        "hotel_video": ["hotel-samosir-cottages", "hotel-hope-villa-2d1n"],
        "foto_atas": 3,
        "judul": "Explore Danau Toba 2D1N — Jelajahwisatasumatera",
        "deskripsi": "Paket Private Trip 2 Hari 1 Malam ke Danau Toba bersama Jelajah Wisata Sumatera. Pengalaman eksklusif dengan dokumentasi drone profesional.",
        "og_judul": "Explore Danau Toba 2D1N — Jelajah Wisata Sumatera",
        "og_deskripsi": "Paket liburan premium 2 Hari 1 Malam ke Danau Toba. Harga terbaik sudah termasuk dokumentasi lengkap!",
        "wa_teks": "Halo, saya tertarik dengan Paket Trip 2D1N Danau Toba",
        "judul_hotel": "(VIDEO HOTEL YANG AKAN DIGUNAKAN)<br>(BOLEH PILIH SALAH SATU HOTEL YA)",
        "label_hotel": ["OPSI PERTAMA<br>SAMOSIR COTTAGES", "OPSI KEDUA<br>HOPE VILLA"],
        "hotel": [],
        "switzerland": False,
        "robots": "index, follow",
    },
    "3d2n": {
        "hotel_video": ["hotel-samosir-cottages", "hotel-hope-villa"],
        "foto_atas": 3,
        "judul": "Explore Danau Toba 3D2N — Jelajahwisatasumatera",
        "deskripsi": "Paket Private Trip 3 Hari 2 Malam ke Danau Toba bersama Jelajah Wisata Sumatera. Pengalaman eksklusif dengan dokumentasi drone profesional.",
        "og_judul": "Explore Danau Toba 3D2N — Jelajah Wisata Sumatera",
        "og_deskripsi": "Paket liburan premium 3 Hari 2 Malam ke Danau Toba. Harga terbaik sudah termasuk dokumentasi lengkap!",
        "wa_teks": "Halo, saya tertarik dengan Paket Trip 3D2N Danau Toba",
        "hotel": ["Samosir Cottages", "Hope Villa"],
        "switzerland": False,
        "robots": "index, follow",
    },
    "4d3n": {
        "hotel_video": ["hotel-ello", "hotel-hope-villa", "hotel-samosir-cottages"],
        "foto_atas": 3,
        "judul": "Explore Danau Toba 4D3N — Jelajahwisatasumatera",
        "deskripsi": "Paket Private Trip 4 Hari 3 Malam ke Danau Toba bersama Jelajah Wisata Sumatera. Pengalaman eksklusif dengan dokumentasi drone profesional.",
        "og_judul": "Explore Danau Toba 4D3N — Jelajah Wisata Sumatera",
        "og_deskripsi": "Paket liburan premium 4 Hari 3 Malam ke Danau Toba. Harga terbaik sudah termasuk dokumentasi lengkap!",
        "wa_teks": "Halo, saya tertarik dengan Paket Trip 4D3N Danau Toba",
        "hotel": ["Ello Hotel", "Hope Villa", "Samosir Cottages"],
        "switzerland": True,
        "robots": "index, follow",
    },
    "5d4n": {
        "hotel_video": ["hotel-ello", "hotel-hope-villa",
                        "hotel-camping-holbung", "hotel-samosir-cottages"],
        "foto_atas": 3,
        "judul": "Explore Danau Toba 5D4N — Jelajahwisatasumatera",
        "deskripsi": "Paket Private Trip 5 Hari 4 Malam ke Danau Toba bersama Jelajah Wisata Sumatera. Pengalaman eksklusif dengan dokumentasi drone profesional.",
        "og_judul": "Explore Danau Toba 5D4N — Jelajah Wisata Sumatera",
        "og_deskripsi": "Paket liburan premium 5 Hari 4 Malam ke Danau Toba. Harga terbaik sudah termasuk dokumentasi lengkap!",
        "wa_teks": "Halo, saya tertarik dengan Paket Trip 5D4N Danau Toba",
        "hotel": ["Ello Hotel", "Hope Villa", "Camping Holbung", "Samosir Cottages"],
        "switzerland": True,
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

        /* ── Fade-in iframe YouTube saat baru dimasukkan ── */
        .vid-card iframe {
            animation: vid-muncul 0.35s ease;
        }
        @keyframes vid-muncul {
            from { opacity: 0; }
            to   { opacity: 1; }
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

        /* Sampul yang bisa diklik + iframe pengganti berbagi ukuran yang sama,
           supaya tinggi kartu tidak berubah sedikit pun saat video dimuat. */
        .vid-card .vid-play,
        .vid-card iframe {
            width: 100%;
            aspect-ratio: 9 / 16;
            border-radius: 8px;
            background: #111;
            display: block;
            border: 0;
        }

        .vid-card .vid-play {
            position: relative;
            padding: 0;
            cursor: pointer;
            overflow: hidden;
            -webkit-tap-highlight-color: transparent;
        }

        .vid-card .vid-play img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
        }

        /* Tombol play — segitiga putih di dalam bulatan gelap */
        .vid-card .vid-play-ikon {
            position: absolute;
            top: 50%;
            left: 50%;
            width: 52px;
            height: 52px;
            margin: -26px 0 0 -26px;
            border-radius: 50%;
            background: rgba(0, 0, 0, 0.55);
            border: 2px solid rgba(255, 255, 255, 0.9);
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.45);
            transition: transform 0.2s ease, background 0.2s ease;
        }
        .vid-card .vid-play-ikon::after {
            content: "";
            position: absolute;
            top: 50%;
            left: 54%;
            transform: translate(-50%, -50%);
            border-style: solid;
            border-width: 9px 0 9px 15px;
            border-color: transparent transparent transparent #fff;
        }
        .vid-card .vid-play:hover .vid-play-ikon,
        .vid-card .vid-play:focus-visible .vid-play-ikon {
            transform: scale(1.08);
            background: rgba(0, 0, 0, 0.75);
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
        // Kartu video tampil sebagai gambar sampul dulu; iframe YouTube baru
        // dipasang saat diklik, supaya membuka halaman tidak ikut mengunduh
        // sebelas player sekaligus.
        document.addEventListener('DOMContentLoaded', () => {
            let main = null;   // { tombol, iframe } yang sedang diputar

            // Kembalikan kartu yang sedang main ke wujud sampulnya. Ini juga
            // yang menghentikan videonya — iframe-nya memang dibuang, jadi
            // tidak ada player yang diam-diam terus jalan di latar.
            const tutup = () => {
                if (!main) return;
                main.iframe.replaceWith(main.tombol);
                main = null;
            };

            document.querySelectorAll('.vid-play').forEach(tombol => {
                tombol.addEventListener('click', () => {
                    tutup();   // hanya satu video boleh main sekaligus

                    const id = tombol.dataset.yt;
                    const iframe = document.createElement('iframe');
                    // nocookie: YouTube tidak menaruh cookie pelacak sebelum
                    // pengunjung benar-benar menonton.
                    // loop butuh playlist berisi ID yang sama — itu memang
                    // cara YouTube, bukan salah tulis.
                    iframe.src = 'https://www.youtube-nocookie.com/embed/' + id +
                        '?autoplay=1&playsinline=1&rel=0&modestbranding=1' +
                        '&loop=1&playlist=' + id;
                    iframe.title = tombol.getAttribute('aria-label') || 'Video';
                    iframe.allow = 'accelerometer; autoplay; encrypted-media; ' +
                        'gyroscope; picture-in-picture; web-share';
                    iframe.allowFullscreen = true;
                    iframe.loading = 'lazy';

                    tombol.replaceWith(iframe);
                    main = { tombol, iframe };
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


def id_youtube(nama):
    """ID YouTube untuk satu video, dari peta YOUTUBE.

    `nama` boleh berupa jalur ('assets/video/hotel-ello') atau nama saja —
    yang dipakai cuma bagian terakhirnya.

    Sengaja berhenti dengan galat kalau ID-nya kosong: lebih baik build gagal
    dengan pesan jelas daripada menghasilkan halaman berisi kartu yang tidak
    bisa diputar, karena kartu mati baru ketahuan setelah tayang.
    """
    kunci = os.path.basename(nama)
    if kunci not in YOUTUBE:
        raise SystemExit(
            f"[GAGAL] '{kunci}' belum ada di peta YOUTUBE di build_trip.py."
        )
    vid = YOUTUBE[kunci].strip()
    if not vid:
        raise SystemExit(
            f"[GAGAL] ID YouTube untuk '{kunci}' masih kosong.\n"
            f"        Unggah assets/video/{kunci}-web.mp4 ke YouTube sebagai\n"
            f"        Unlisted, lalu isi ID-nya di peta YOUTUBE di build_trip.py."
        )
    return vid


def kartu_video(label, nama):
    """Satu kartu video: sampul yang bisa diklik, iframe menyusul kemudian.

    Yang keluar bukan <iframe>, melainkan <button> berisi gambar sampul.
    Skrip di bawah halaman menukarnya jadi iframe YouTube saat diklik — lihat
    alasannya di komentar FOLDER_POSTER.
    """
    kunci = os.path.basename(nama)
    vid = id_youtube(kunci)
    poster = f"{FOLDER_POSTER}/{kunci}.webp"
    if not os.path.exists(poster):
        raise SystemExit(
            f"[GAGAL] sampul {poster} tidak ada.\n"
            f"        Buat dengan: ffmpeg -ss 1 -i assets/video/{kunci}-web.mp4 "
            f"-frames:v 1 -vf scale=540:-2 -q:v 72 {poster}"
        )
    # Label dipakai ulang jadi teks alt, tapi <br> di dalamnya harus jadi spasi.
    alt = re.sub(r'<br\s*/?>', ' ', label) if label else kunci.replace('-', ' ')
    # Kartu Switzerland tidak berlabel — barisnya dibuang seluruhnya, bukan
    # dibiarkan kosong, karena .vid-label punya min-height yang akan menyisakan
    # celah di atas videonya.
    baris_label = f'                <div class="vid-label">{label}</div>\n' if label else ''
    return f"""            <div class="vid-card">
{baris_label}                <button class="vid-play" data-yt="{vid}" aria-label="Putar video {alt}">
                    <img src="{poster}" alt="{alt}" loading="lazy" decoding="async" width="540" height="960">
                    <span class="vid-play-ikon" aria-hidden="true"></span>
                </button>
            </div>
"""


def blok_hotel(cfg):
    berkas = list(cfg["hotel_video"])
    jumlah = len(berkas)
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
            out += kartu_video(label, f"{FOLDER_VIDEO}/{berkas[n]}")
        out += '        </div>\n'
    out += f'\n        <p class="frame-note">{TEKS_HOTEL_BAWAH}</p>\n'
    out += '    </div>\n'
    return out


def blok_switzerland(cfg):
    if not cfg.get("switzerland"):
        return ""
    return f"""
    <!-- ══════════════════════════════════════════════════════════════ -->
    <!-- BLOK VIDEO SWITZERLAND DANAU TOBA                              -->
    <!-- ══════════════════════════════════════════════════════════════ -->
    <div class="custom-frame drone-screen-1">
        <p class="swiss-intro">{TEKS_SWISS}</p>

        <div class="solo-grid">
{kartu_video("", f"{FOLDER_VIDEO}/switzerland")}        </div>
    </div>
"""


def blok_drone(cfg):
    label = cfg.get("label_drone") or LABEL_DRONE

    def src(n):
        return f"{FOLDER_VIDEO}/drone-{n}"

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
{blok_foto(paket, atas, 'FOTO BAGIAN ATAS', prioritas_pertama=True)}{blok_hotel(cfg)}{blok_drone(cfg)}{blok_switzerland(cfg)}{blok_foto(paket, bawah, 'FOTO BAGIAN BAWAH')}
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
    for nama_berkas in cfg["hotel_video"]:
        cek(os.path.join(FOLDER_VIDEO, nama_berkas), hilang)
    for n in range(1, 6):
        cek(os.path.join(FOLDER_VIDEO, f"drone-{n}"), hilang)
    if cfg.get("switzerland"):
        cek(os.path.join(FOLDER_VIDEO, "switzerland"), hilang)
    print(f"  video: {len(cfg['hotel_video'])} hotel + 5 drone"
          + (" + switzerland" if cfg.get("switzerland") else "")
          + f" (semua dari {FOLDER_VIDEO}/)")
    if not frames:
        print(f"  ! belum ada frame-NN.webp di {folder_aset}/ — halaman masih tanpa foto")
    for p in hilang:
        print(f"  ! video belum ada: {p}")


def periksa():
    """Pastikan tidak ada video yang tersimpan dua kali dengan isi sama.

    Dulu tiap paket punya salinan videonya sendiri, jadi satu hotel bisa
    tersimpan sampai 4 kali dengan alamat berbeda. Sejak video disemat dari
    YouTube itu tidak lagi memakan kuota, tapi tetap merepotkan: tiap salinan
    berarti satu unggahan lagi dan satu ID lagi yang harus diurus, dan kalau
    videonya diperbarui gampang ada yang tertinggal.

    Sekalian fungsi ini memastikan tiap video punya ID YouTube dan sampulnya.

    Perbandingan md5 saja tidak cukup: video yang sama bisa dikompres terpisah
    dari wadah berbeda (.mp4 vs .mov) dan menghasilkan byte yang lain. Karena
    itu isi video dibandingkan lewat durasi + jumlah frame dari ffprobe.
    """
    masalah = 0

    # 1. Video apa yang dipakai paket mana.
    #
    # Dulu ini dibaca dengan mencari '.mp4' di dalam trip-*.html. Sejak video
    # disemat dari YouTube, halaman tidak lagi menyebut nama berkas sama sekali,
    # jadi daftarnya dibaca langsung dari PAKET di berkas ini.
    rujuk = {}
    for paket, cfg in PAKET.items():
        dipakai = list(cfg["hotel_video"]) + [f"drone-{n}" for n in range(1, 6)]
        if cfg.get("switzerland"):
            dipakai.append("switzerland")
        for nama in dipakai:
            rujuk.setdefault(f"{FOLDER_VIDEO}/{nama}-web.mp4", []).append(paket)

    print(f"{sum(len(v) for v in rujuk.values())} rujukan video "
          f"-> {len(rujuk)} berkas unik")

    # 2. Tiap video harus punya berkasnya, ID YouTube-nya, dan sampulnya
    for u in sorted(rujuk):
        nama = os.path.basename(u)[:-len('-web.mp4')]
        if not os.path.exists(u):
            print(f"  ! tidak ada di komputer ini: {u}")
            masalah += 1
        if not YOUTUBE.get(nama, "").strip():
            print(f"  ! ID YouTube masih kosong: {nama}")
            masalah += 1
        sampul = f"{FOLDER_POSTER}/{nama}.webp"
        if not os.path.exists(sampul):
            print(f"  ! sampul belum dibuat: {sampul}")
            masalah += 1

    # 2b. Entri peta yang tidak dipakai paket mana pun — biasanya sisa video
    #     lama yang sudah dilepas, atau salah ketik nama.
    terpakai = {os.path.basename(u)[:-len('-web.mp4')] for u in rujuk}
    for nama in sorted(set(YOUTUBE) - terpakai):
        print(f"  ! ada di peta YOUTUBE tapi tidak dipakai paket mana pun: {nama}")
        masalah += 1

    # 3. Tidak boleh ada dua berkas berbeda yang isinya sama
    sidik = {}
    for u in sorted(rujuk):
        if not os.path.exists(u):
            continue
        try:
            hasil = subprocess.run(
                ['ffprobe', '-v', 'error', '-select_streams', 'v:0',
                 '-show_entries', 'stream=nb_frames,width,height',
                 '-show_entries', 'format=duration', '-of', 'csv=p=0', u],
                check=True, capture_output=True)
            kunci = hasil.stdout.decode(errors='ignore').strip()
        except Exception:
            continue                      # ffprobe tidak ada — lewati saja
        if kunci in sidik:
            print(f"  ! isinya sama dengan {sidik[kunci]}: {u}")
            print(f"      satukan jadi satu berkas, lalu tunjuk dari "
                  f"\"hotel_video\" kedua paket")
            masalah += 1
        else:
            sidik[kunci] = u

    # 4. Video di folder tapi tidak dipakai siapa pun
    if os.path.isdir(FOLDER_VIDEO):
        di_disk = {f"{FOLDER_VIDEO}/{f}" for f in os.listdir(FOLDER_VIDEO)
                   if f.endswith('.mp4')}
        for u in sorted(di_disk - set(rujuk)):
            print(f"  ! ada di folder tapi tidak dipakai halaman mana pun: {u} "
                  f"({os.path.getsize(u)/10**6:.0f} MB)")
            masalah += 1

    # 5. Daftar unggahan: berkas mana, dipakai paket mana, ID-nya sudah ada belum
    total = sum(os.path.getsize(u) for u in rujuk if os.path.exists(u))
    print(f"\n{len(rujuk)} video / {total/10**6:.0f} MB untuk diunggah ke YouTube:")
    for u in sorted(rujuk):
        nama = os.path.basename(u)[:-len('-web.mp4')]
        vid = YOUTUBE.get(nama, "").strip()
        print(f"  {os.path.basename(u):<34} {len(rujuk[u])} paket "
              f"({', '.join(rujuk[u])})  {vid or '— ID belum diisi'}")

    print()
    if masalah:
        print(f"! {masalah} masalah ditemukan.")
    else:
        print("Bersih: satu video = satu berkas = satu ID YouTube.")
    return 1 if masalah else 0


if __name__ == '__main__':
    if '--periksa' in sys.argv:
        sys.exit(periksa())

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
