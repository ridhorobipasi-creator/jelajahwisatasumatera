# Jelajah Wisata Sumatera

Website PT Jelajah Wisata Sumatera — private trip & group tour Danau Toba, Tangkahan,
Mursala Kalimantung, dan Aceh Sabang.

Website statis (HTML + CSS + JS langsung di dalam file, tanpa framework).
Tidak perlu install apa-apa untuk melihat hasilnya — cukup buka filenya di browser.

---

## Isi folder

| File / folder | Keterangan |
|---|---|
| `index.html` | Halaman depan (gaya linktree): profil, tombol paket, link sosmed |
| `blog.html` | Profil perusahaan, 4 destinasi, contoh itinerary |
| `trip-2d1n.html` … `trip-5d4n.html` | Halaman detail tiap paket — **dibuat otomatis, jangan diedit manual** |
| `build_trip.py` | Generator halaman paket |
| `prepare_assets.py` | Rename + konversi + kompres foto & video |
| `deploy.bat` | Commit + push ke GitHub sekali klik |
| `assets/` | Foto & video yang dipakai website |
| `assets/<paket>/_masuk/` | **Tempat menaruh file mentah** sebelum diproses |
| `_sumber/` | Arsip bahan mentah (PDF, foto & video asli). Tidak ikut ke GitHub |

---

## Cara memperbarui isi satu paket

Contoh untuk paket 4D3N:

**1. Taruh file mentah** ke `assets/4d3n/_masuk/`

- **Foto** — nama bebas, urutan tampil di web mengikuti urutan nama file.
  Contoh: `01-cover.png`, `02-pricelist.png`, `03-include.png`, …
- **Video** — nama **harus** mengandung kata `hotel` atau `drone`.
  Contoh: `hotel-1.mp4`, `hotel-2.mov`, `drone-1.mp4`

**2. Proses filenya**

```
python prepare_assets.py 4d3n
```

Foto jadi `frame-01.webp`, `frame-02.webp`, … dan video jadi
`hotel-day1-web.mp4`, `drone-1-web.mp4`, … sekaligus dikompres.
Tambahkan `--dry` kalau mau lihat rencananya dulu tanpa mengubah apa pun.

**3. Bangun halamannya**

```
python build_trip.py 4d3n
```

Bisa juga sekaligus: `python build_trip.py semua`

**4. Cek hasilnya di browser**

```
python -m http.server 5000
```

Lalu buka <http://localhost:5000>

**5. Upload ke GitHub** — klik dua kali `deploy.bat`

---

## Mengubah teks halaman paket

Judul, deskripsi SEO, nama hotel per malam, dan posisi blok video diatur di
bagian `PAKET` pada `build_trip.py`. Setelah diubah, jalankan ulang
`python build_trip.py <paket>`.

Susunan halaman tiap paket sama:

```
tombol kembali
foto 1–3
blok video hotel   (1 video per malam)
blok video drone   (5 video)
sisa foto
tombol WhatsApp melayang
```

Jumlah foto boleh beda-beda tiap paket — dideteksi otomatis.
Ingin blok video muncul setelah foto ke-4 (bukan ke-3)? Ubah `foto_atas` di `build_trip.py`.

---

## Yang perlu dipasang (hanya untuk memproses aset)

- **Python 3** + Pillow → `pip install Pillow`
- **FFmpeg** → untuk kompres video, harus bisa dipanggil dari terminal

---

## Catatan ukuran file

Video yang di-hosting sendiri sebaiknya **pendek (10–30 detik) dan di bawah 10 MB**.
`prepare_assets.py` sudah otomatis menurunkan resolusi ke lebar maks 1080px dan
mengompres. Untuk video panjang, lebih baik diunggah ke YouTube lalu disematkan,
supaya tidak membebani hosting dan kuota bandwidth.
