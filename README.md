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
| `upload_blob.py` | Bekas alur Vercel Blob — **sudah tidak dipakai**, video kini dari YouTube |
| `deploy.bat` | Commit + push ke GitHub sekali klik |
| `assets/<paket>/` | Foto paket (`frame-01.webp`, …) |
| `assets/video/` | **Semua video, satu folder untuk semua paket** — arsip lokal, tidak ikut ke GitHub |
| `assets/poster/` | Gambar sampul kartu video (dibuat dari video di atas) |
| `assets/<paket>/_masuk/` | Tempat menaruh **foto** mentah |
| `assets/video/_masuk/` | Tempat menaruh **video** mentah |
| `_sumber/` | Arsip: PDF, pricelist resolusi penuh, kiriman asli klien di `dari-klien/`. Tidak ikut ke GitHub |

---

## Foto per paket, video satu folder

Foto beda-beda tiap paket, tapi **video hotel banyak yang dipakai bersama** —
Samosir Cottages misalnya muncul di keempat paket. Karena itu video tidak
disalin per paket. Satu video = satu berkas = satu alamat, dinamai menurut
isinya (`hotel-samosir-cottages-web.mp4`), bukan menurut hari ke berapa ia
muncul di sebuah paket.

Dulu tidak begitu, dan akibatnya mahal: berkas yang sama tersimpan sampai 4 kali
(918 MB simpanan padahal isinya cuma 671 MB), dan pengunjung yang membandingkan
beberapa paket mengunduh video yang sama berulang kali karena browser
melihatnya sebagai alamat berbeda.

---

## Cara memperbarui foto satu paket

Contoh untuk paket 4D3N:

**1. Taruh foto mentah** ke `assets/4d3n/_masuk/`

Nama bebas, urutan tampil di web mengikuti urutan nama file.
Contoh: `01-cover.png`, `02-pricelist.png`, `03-include.png`, …

**2. Proses filenya**

```
python prepare_assets.py 4d3n
```

Foto jadi `frame-01.webp`, `frame-02.webp`, … sekaligus dikompres.
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

**5. Video: unggah ke YouTube, isi ID-nya**

Video tidak ikut ke GitHub (berkasnya jauh di atas batas 100 MB per file) dan
tidak lagi dilayani sendiri — halaman menyematnya dari YouTube. Jadi setiap
video baru harus diunggah ke YouTube sebagai **Unlisted**, lalu ID-nya diisi ke
peta `YOUTUBE` di `build_trip.py`. Lihat bagian "Video disemat dari YouTube"
di bawah.

`python build_trip.py` menolak jalan selama masih ada ID yang kosong, jadi
langkah ini tidak bisa terlewat diam-diam.

**6. Upload ke GitHub** — klik dua kali `deploy.bat`

---

## Cara menambah atau mengganti video

**1. Taruh video mentah** ke `assets/video/_masuk/`

Nama berkasnya **jadi** nama video di web, jadi beri nama menurut isinya:

```
hotel-ello.mov   ->  assets/video/hotel-ello-web.mp4
drone-1.mp4      ->  assets/video/drone-1-web.mp4
```

**2. Proses**

```
python prepare_assets.py video
```

**3. Daftarkan ke paket yang memakainya** — buka `build_trip.py`, bagian `PAKET`,
isi `hotel_video` sesuai urutan malam:

```python
"5d4n": {
    "hotel_video": ["hotel-ello", "hotel-hope-villa",
                    "hotel-camping-holbung", "hotel-samosir-cottages"],
    "hotel":       ["Ello Hotel", "Hope Villa",
                    "Camping Holbung", "Samosir Cottages"],
```

Paket yang menginap di hotel sama cukup menyebut berkas yang sama — di situlah
penghematannya. Video drone dipakai semua paket, jadi tidak perlu diatur.

**4. Unggah ke YouTube (Unlisted), isi ID-nya** ke peta `YOUTUBE` di
`build_trip.py` — lihat bagian berikutnya.

**5. Buat gambar sampulnya**

```
ffmpeg -ss 1 -i assets/video/NAMA-web.mp4 -frames:v 1 -vf scale=540:-2 -q:v 72 assets/poster/NAMA.webp
```

**6. Bangun ulang + kirim** — `python build_trip.py semua`, lalu `deploy.bat`.

### Memeriksa tidak ada video kembar

```
python build_trip.py --periksa
```

Menjawab sekaligus: adakah berkas yang dirujuk tapi hilang, adakah video yang
belum punya ID YouTube atau belum punya sampul, adakah **dua berkas berbeda yang
isinya sama**, dan adakah video yang menganggur tak dipakai halaman mana pun.
Keluar dengan kode 1 kalau ada masalah, jadi bisa dipakai sebagai penjaga
sebelum deploy.

Perbandingan isinya memakai durasi + jumlah frame dari `ffprobe`, **bukan md5**.
Itu penting: video yang sama bisa dikompres terpisah dari wadah berbeda
(`.mp4` vs `.mov`) dan menghasilkan byte yang lain sama sekali — dulu satu video
hotel tersimpan 4 kali dan md5-nya berbeda-beda semua, jadi tidak ketahuan.

---

## Video disemat dari YouTube

Halaman tidak melayani videonya sendiri. Tiap video diunggah ke YouTube, lalu
ID-nya — potongan 11 huruf di `https://youtu.be/XXXXXXXXXXX` — diisi ke peta
`YOUTUBE` di `build_trip.py`:

```python
YOUTUBE = {
    "hotel-samosir-cottages":  "AbCdEfGhIjK",
    ...
}
```

Kuncinya nama berkas di `assets/video/` **tanpa akhiran `-web`**. Kalau ada yang
kosong, `build_trip.py` berhenti dengan pesan yang menyebut nama berkasnya —
bukan menghasilkan halaman berisi kartu mati.

Video harus **Unlisted** atau Public. **Private tidak bisa disemat** — hasilnya
kotak hitam.

### Kartu video: sampul dulu, player menyusul

Yang dipasang di halaman bukan `<iframe>`, melainkan gambar sampul dari
`assets/poster/` yang bisa diklik. Iframe YouTube baru dibuat saat pengunjung
menekan play. Sebelas iframe sekaligus berarti sebelas player ikut diunduh
begitu halaman dibuka — berat sekali di HP; dengan sampul, yang dimuat awalnya
cuma gambar ±40 KB.

Sampul dibuat dari video lokal (bukan thumbnail bawaan YouTube, yang memberi
bilah hitam kiri-kanan pada video tegak 9:16), ikut ke GitHub, dan dilayani
Vercel.

Efek sampingnya bagus: hanya satu video bisa main sekaligus, karena membuka
video lain mengembalikan yang sebelumnya jadi sampul — iframe-nya dibuang, jadi
tidak ada player yang diam-diam terus jalan di latar.

### Kenapa pindah dari Vercel Blob

Dulu video dilayani sendiri lewat Vercel Blob. Itu mati pada **2026-08-02**, dan
yang menjatuhkannya **bukan** kuota simpanan melainkan **kuota transfer**: paket
Hobby memberi 10 GB/bulan, terpakai **21,4 GB dalam 5 hari**, dan Vercel
memblokir seluruh store — semua video di keempat paket mati serentak dengan
balasan `403 Your store is blocked`. Simpanan waktu itu masih 703 MB dari 1 GB
alias belum jebol sama sekali.

Sebabnya sederhana: satu halaman paket memanggil ratusan MB video, jadi belasan
pengunjung yang menonton lengkap sudah menghabiskan jatah sebulan. Artinya situs
yang laku justru yang paling cepat mati — dan mengecilkan video cuma menunda,
tidak menyelesaikan.

YouTube tidak menagih transfer sama sekali, jadi masalah itu tidak bisa terulang
berapa pun ramainya pengunjung.

`upload_blob.py` ditinggal sebagai catatan sejarah dan sudah tidak dipakai alur
mana pun.

---

## Mengubah teks halaman paket

Judul, deskripsi SEO, nama hotel per malam, video hotel mana yang dipakai
(`hotel_video`), dan posisi blok video diatur di bagian `PAKET` pada
`build_trip.py`. Setelah diubah, jalankan ulang `python build_trip.py <paket>`.

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
