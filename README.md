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
| `upload_blob.py` | Unggah video ke Vercel Blob — **video tidak lewat GitHub** |
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

**5. Unggah videonya**

```
python upload_blob.py
```

**Langkah ini tidak boleh dilewat.** Video sengaja tidak ikut ke GitHub —
berkasnya jauh di atas batas 100 MB per file yang dipaksakan GitHub, jadi
halaman memanggilnya lewat Vercel Blob. `deploy.bat` di langkah 6 hanya
mengirim HTML dan foto; kalau langkah ini dilewat, halaman akan menunjuk
alamat video yang tidak ada isinya dan semua video jadi kotak hitam.

Aman dijalankan berulang — yang sudah terunggah dilewati. Tambahkan `--dry`
untuk melihat rencananya dulu.

**6. Upload ke GitHub** — klik dua kali `deploy.bat`

---

## Batas 1 GB video

Paket Hobby Vercel Blob cuma memberi **1 GB untuk seluruh video** di situs ini.
Per 2026-07-28 terpakai sekitar 918 MB, jadi sisanya tinggal ~106 MB.

`upload_blob.py` menolak jalan kalau totalnya melewati batas, lengkap dengan
daftar berkas paling boros — lebih baik ketahuan di awal daripada unggahan
berhenti di tengah dan sebagian video mati diam-diam.

Kalau kelebihan, pilihannya:

- Kecilkan video yang paling boros (turunkan `MAXRATE` di `prepare_assets.py`,
  lalu proses ulang paketnya)
- Naik ke paket berbayar, lalu naikkan `BATAS_BYTE` di `upload_blob.py`

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

`prepare_assets.py` mengompres video ke H.264 dengan `CRF = 23` dan atap bitrate
`MAXRATE = 4M`, tapi **resolusinya dibiarkan apa adanya** (`LEBAR_MAKS = None`) —
video vertikal 1080×1920 tetap 1080×1920. Hasilnya sekitar 13–132 MB per video,
bukan angka kecil.

Kalau butuh jauh lebih ringan, ada dua tuas di `prepare_assets.py`:

- Turunkan `MAXRATE` (mis. `'2M'`) — cara paling langsung mengecilkan berkas
- Isi `LEBAR_MAKS` (mis. `720`) — turunkan resolusinya sekalian

Untuk video yang sangat panjang, menyematkan dari YouTube tetap lebih hemat
daripada menaruhnya di Blob, karena kuota simpanan **dan** kuota transfer
sama-sama terpakai setiap kali pengunjung menekan play.
