# E-Learning Activity Tracker (FastAPI)

FastAPI service for managing student records and running simple learning-activity analytics on top of a MySQL database. It ships with JWT authentication (admin + student roles), student CRUD helpers, analytics endpoints, and a CSV import script to seed the database.

## Project layout
- `main.py` – FastAPI app factory and router registration
- `auth.py` – OAuth2 password flow, JWT issuance/verification, admin & student guards
- `database.py` – SQLAlchemy engine/session configuration
- `modules/items/models.py` – `Student` ORM model
- `modules/items/routes/` – student CRUD and analytics routes
- `import_students.py` – CSV seeder for `data/students_kaggle.csv`

## Prerequisites
- Python 3.10+
- MySQL instance you can reach from the app (local or remote)

## Quickstart (umum)
1. Buat dan aktifkan virtual environment.
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\\Scripts\\activate
   ```
2. Install dependencies.
   ```bash
   pip install -r requirements.txt
   ```
3. Salin `.env.example` ke `.env` lalu sesuaikan kredensial DB dan secret.
   ```bash
   cp .env.example .env
   # ekspor variabel untuk shell saat ini (bash/zsh)
   set -a; source .env; set +a
   ```
4. Pastikan MySQL berjalan dan DB yang dirujuk di `.env` sudah ada (tabel otomatis dibuat saat start).
5. (Opsional) Import dataset Kaggle:
   ```bash
   python import_students.py
   ```
6. Jalankan API:
   ```bash
   uvicorn main:app --reload
   ```
   Docs interaktif: `http://localhost:8000/docs`.






## Menjalankan di macOS (Homebrew)
1. Install Python 3.12: `brew install python@3.12` (atau pakai pyenv 3.12).
2. Clone repo dan masuk: `git clone <repo> && cd <repo>`.
3. Salin env: `cp .env.example .env` lalu edit MySQL creds (`127.0.0.1` disarankan).
4. Buat/aktifkan venv: `python3.12 -m venv .venv && source .venv/bin/activate`.
5. Install deps: `pip install --upgrade pip setuptools wheel && pip install -r requirements.txt`.
6. Export env: `set -a; source .env; set +a`.
7. (Opsional) Seed data: `python import_students.py`.
8. Start API: `uvicorn main:app --reload`.

## Menjalankan di Windows (Command Prompt/PowerShell)
1. Pastikan Python 3.10+ terpasang dan ada di PATH.
2. Clone repo dan masuk foldernya.
3. Salin env: `copy .env.example .env` lalu edit kredensial MySQL.
4. Buat/aktifkan venv:
   - Command Prompt: `python -m venv venv` lalu `venv\Scripts\activate`
   - PowerShell: `python -m venv venv` lalu `.\venv\Scripts\Activate.ps1`
5. Install deps: `pip install --upgrade pip setuptools wheel && pip install -r requirements.txt`.
6. Set env (contoh Command Prompt):
   ```bat
   for /f "tokens=1,2 delims==" %i in (.env) do set %i=%j
   ```
   PowerShell:
   ```powershell
   Get-Content .env | ForEach-Object {
     if ($_ -match "^(.*?)=(.*)$") { [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2]) }
   }
   ```
   Atau set manual variabel penting (MYSQL_*, JWT_SECRET_KEY, dll.).
7. (Opsional) Seed data: `python import_students.py`.
8. Jalankan API: `uvicorn main:app --reload`.





## Authentication
- Obtain a token: `POST /auth/login` with form data `username` and `password` (admin defaults come from `.env`).
- Pass the token as `Authorization: Bearer <token>` for protected endpoints.
- Student accounts can log in after a password is set via `POST /students/{student_id}/password` (admin only).

## Available endpoints (high level)
- `POST /auth/login`, `GET /auth/me`
- CRUD mahasiswa:
  - `GET /students` (admin) – daftar mahasiswa.
  - `GET /students/id/{id}` (admin) – detail via primary key.
  - `GET /students/{student_id}` (admin atau student diri sendiri) – detail via student_id.
  - `POST /students` (admin) – tambah mahasiswa (opsional set password langsung).
  - `POST /students/{student_id}/password` (admin) – set/reset password mahasiswa.
- Partisipasi:
  - `GET /participations` (admin) – daftar partisipasi + rata-rata, skala 0–6.
  - `GET /participations/good|average|bad` (admin) – filter partisipasi (>=75%, 33–75%, <33%).
  - `GET /participations/me` (student) – partisipasi diri sendiri.
- Analitik belajar & aktivitas:
  - `GET /analytics/study-duration` (admin) – rata-rata jam belajar keseluruhan & per jurusan.
  - `GET /analytics/study-duration/{department}` (admin) – detail jam belajar + metrik terkait di jurusan.
  - `GET /analytics/study-duration/{department}/{student_name}` (admin) – cari mahasiswa di jurusan.
  - `GET /analytics/study-duration/me` (student) – jam belajar & metrik terkait diri sendiri.
  - `GET /analytics/activity-correlation/final-score` (admin) – korelasi Pearson antara final_score dan aktivitas (quizzes, study hours, attendance, sleep, ekstra).
  - `GET /analytics/activity-correlation/final-score/me` (student) – melihat hasil korelasi agregat.
  - `GET /analytics/low-activity` (admin) – identifikasi mahasiswa aktivitas rendah konsisten (ambang persentil 25, min_low_metrics dapat diatur).
  - `GET /analytics/activity-trend` (admin) – tren midterm → final (top improving/declining).
  - `GET /analytics/activity-trend/{student_id}` (admin) – tren midterm → final per mahasiswa.

## Environment variables
Configure these in `.env` (or your process manager):

- `DATABASE_URL` (optional) – full SQLAlchemy URL; overrides the fields below when set.
- `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_DB` – MySQL connection pieces used when `DATABASE_URL` is not provided.
- `JWT_SECRET_KEY` – secret key for signing JWTs.
- `ACCESS_TOKEN_EXPIRE_MINUTES` – token lifetime in minutes.
- `ADMIN_USERNAME`, `ADMIN_PASSWORD` – default admin credentials for `POST /auth/login`.

## Notes
- Tables are created automatically when the app starts (`Base.metadata.create_all`).
- The CSV seeder expects `data/students_kaggle.csv` with the included column names.
- If you run without exporting the `.env` file, the defaults in code will be used instead.
