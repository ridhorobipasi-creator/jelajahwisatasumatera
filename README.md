# jelajahwisatasumatera
Btw kalau video di website ada limit waktu pemutaran video bang?
7:52 AM
Halo! Jawaban singkatnya: Secara bawaan (dari sisi kode HTML), tidak ada limit waktu pemutaran video di website. Tag <video> pada HTML5 bisa memutar video dengan durasi 10 detik maupun 10 jam tanpa masalah.

Namun, limitasinya justru datang dari sisi server, ukuran file, dan performa. Berikut adalah beberapa hal yang menjadi "limit" atau batasan di dunia nyata:

1. Batasan Ukuran File (File Size) & Penyimpanan (Storage)
Jika kamu mengunggah (hosting) video tersebut langsung ke server kodemu (misalnya di folder public atau assets), server tempat kamu meletakkan website (seperti Hostinger, Vercel, Netlify) biasanya punya batasan ukuran maksimal file. Video berdurasi panjang dengan resolusi tinggi (misal 1080p atau 4K) akan menghasilkan ukuran file bergiga-giga (GB).

2. Batasan Kuota Bandwidth (Data Transfer)
Setiap kali ada pengunjung yang menonton videomu, server harus mengirim data video tersebut ke perangkat mereka. Jika videomu ukurannya 500MB dan ditonton oleh 100 orang, kamu sudah menghabiskan 50 GB bandwidth. Banyak layanan hosting punya limit bandwidth bulanan; jika terlewati, website-mu bisa mati sementara atau kamu ditagih biaya tambahan.

3. Kecepatan Loading (Performa Website)
Video yang terlalu besar akan membuat website-mu terasa sangat lambat (lemot) saat dimuat, terutama bagi pengunjung yang menggunakan koneksi internet lambat atau dari HP. Ini akan membuat pengunjung kabur sebelum videonya sempat diputar.

Solusi & Best Practice (Praktik Terbaik):
Untuk Video Background / Dekorasi (Misal: di Hero Section halaman depan):

Limit Waktu Ideal: 10 - 30 detik (lalu di-loop/diulang terus menerus).
Ukuran File: Usahakan di bawah 5MB (maksimal banget 10MB).
Cara: Kompres video sekecil mungkin, hilangkan suaranya (muted), dan kurangi resolusinya (misal 720p sudah cukup). Video seperti ini aman di-hosting langsung di file website.
Untuk Video Konten Utama (Durasi Panjang: Menit - Jam):

JANGAN pernah di-hosting sendiri di dalam folder website.
Cara yang Benar: Upload video tersebut ke platform khusus video seperti YouTube, Vimeo, atau layanan cloud CDN. Lalu, Embed (sematkan) videonya ke websitemu menggunakan kode <iframe>.
Keuntungan: Tidak membebani servermu sama sekali, loading sangat cepat, kualitas video otomatis menyesuaikan koneksi internet penonton, dan tidak ada limit durasi.
Apakah untuk website Jelajah Wisata Sumatera ini kamu berencana memasukkan video background di halaman depan, atau video dokumentasi trip yang panjang? Biar saya bisa sarankan cara implementasi terbaiknya.

7:52 AM
ss