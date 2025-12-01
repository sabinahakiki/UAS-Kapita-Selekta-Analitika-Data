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

## Quickstart
1. Create and activate a virtual environment.

   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\\Scripts\\activate
   ```

2. Install dependencies.

   ```bash
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and update the values for your environment.

   ```bash
   cp .env.example .env
   # export variables for this shell
   set -a; source .env; set +a
   ```

4. Ensure your MySQL server is running and that the database in `.env` exists (the tables are auto-created on startup).
5. (Optional) Import the sample Kaggle dataset to populate student rows.

   ```bash
   python import_students.py
   ```

6. Run the API.

   ```bash
   uvicorn main:app --reload
   ```

   The interactive docs are available at `http://localhost:8000/docs`.






## macOS setup (Homebrew)
1. Install Python 3.12: `brew install python@3.12` (or use pyenv with 3.12).
2. Clone the repo and enter it: `git clone <repo> && cd <repo>`.
3. Copy env vars: `cp .env.example .env` then edit with your MySQL creds (`127.0.0.1` host recommended).
4. Create/activate a venv with the Homebrew Python: `python3.12 -m venv .venv && source .venv/bin/activate`.
5. Install deps (includes uvicorn and cryptography for MySQL auth): `pip install --upgrade pip setuptools wheel && pip install -r requirements.txt`.
6. Export env for the shell: `set -a; source .env; set +a`.
7. Run optional seed: `python import_students.py`.
8. Start the API: `python -m uvicorn main:app --reload`.





## Authentication
- Obtain a token: `POST /auth/login` with form data `username` and `password` (admin defaults come from `.env`).
- Pass the token as `Authorization: Bearer <token>` for protected endpoints.
- Student accounts can log in after a password is set via `POST /students/{student_id}/password` (admin only).

## Available endpoints (high level)
- `POST /auth/login`, `GET /auth/me`
- `GET /students/` (list, admin), `GET /students/id/{id}` (admin), `GET /students/{student_id}` (self or admin)
- `POST /students/` (create student, admin)
- `POST /students/{student_id}/password` (set student password, admin)
- Analytics (admin):
  - `GET /analytics/study-duration`
  - `GET /analytics/study-duration/{department}`
  - `GET /analytics/study-duration/{department}/{student_name}`

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
