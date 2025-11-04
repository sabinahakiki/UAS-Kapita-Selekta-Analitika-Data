# UAS-Kapita-Selekta-Analitika-Data
e-learning-activity-tracker/
config/               // Shared: Koneksi DB, JWT Config (Dikerjakan bersama atau oleh Tim 1/Leader)
middlewares/          // Shared: JWT Middleware (Dikerjakan Tim 1)
server.js             // Shared: Titik Masuk Aplikasi (Dikerjakan Leader)
modules/
    Database (ALL)
        -akun (mahasiswa, dosen, staf e-learning)
        -chat_history: chat apa, akun mahasiswa
        -tugas: kode tugas, nilai mahasiswa, akun mahasiswa, mata kuliah apa
        -materi_perkuliahan: pdf, mata kuliah apa
        -aktivitas: lama mahasiswa buka pdf, mata kuliah apa, semester berapa

    Library (ALL)

    Autentifikasi akun
        -Database: akun
        -routes
        -model

    Kegiatan E-Learning (aplikasi)
        -Database: materi_perkuliahan, aktivitas, tugas
        -routes
        -model
            Masukin materi berupa pdf (dosen)
            Lihat materi berupa pdf (mahasiswa & dosen)
            Buat kode tugas (dosen)
            Submit tugas (mahasiswa)
            Liat hasil tugas (dosen)
            Ngasih nilai (dosen)

    Log Aktivitas (proses analisa data)
        -Database: akun, chat_history, tugas, aktivitas
        -routes
        -model
            durasi belajar mahasiswa buka pdf
            banyak komentar mahasiswa di forum diskusi
            peningkatan atau penurunan aktivitas belajar sepanjang semester

    Media Komunikasi
        -Database: chat_history
        -routes
        -model
            forum diskusi
