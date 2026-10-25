# 🎓 Students Database CRUD Application

A production-ready, beginner-friendly RESTful API built with **Python 3**, **FastAPI**, and **SQLAlchemy ORM**, backed by **SQLite** storage and validated with **Pydantic v2**.

This project demonstrates clean architecture patterns, robust HTTP status code handling (201, 204, 404, 409, 422), zero 500 crashes on bad input, idempotent database seeding, automated testing with isolated in-memory databases, and optional local AI integration via Ollama.

---

## 🌟 Key Features

* **Complete CRUD Lifecycle**: Create, Read, Update (full PUT & partial PATCH), and Delete student records.
* **Smart Filtering & Pagination**: Filter students by case-insensitive name, course, or date of birth (`born_after`), along with `skip` and `limit` offset pagination.
* **Strict Input Validation**:
  * Name: 2–100 characters.
  * Date of Birth: Must strictly be a date in the past.
  * Phone Number: Validated 7–15 digits.
  * Email: Verified standard email format via Pydantic `EmailStr`.
  * **Contact Constraint**: At least one contact method (`email` or `phone`) is required.
* **Production Status Code Discipline**:
  * `200 OK`: Successful retrieval and updates.
  * `201 Created`: Successful creation of new student.
  * `204 No Content`: Successful deletion (empty body).
  * `404 Not Found`: When an ID does not exist in the database.
  * `409 Conflict`: Duplicate email or phone collisions.
  * `422 Unprocessable Entity`: Input validation or schema format errors.
  * **Zero 500 Errors**: All edge cases and unique database constraints are safely handled.
* **Idempotent Data Seeder**: `seed.py` inserts 10 sample records and safely skips existing records on repeated runs.
* **Automated Pytest Suite**: 16 isolated unit & integration tests run against an in-memory SQLite database via FastAPI `dependency_overrides`.
* **Optional Local AI Assistant**: Generates personalized academic and career recommendations using local **Ollama** models (`llama3`, `mistral`) with graceful fallback.

---

## 🛠️ Tech Stack

* **Language**: Python 3.10+
* **Web Framework**: [FastAPI](https://fastapi.tiangolo.com/)
* **ASGI Server**: [Uvicorn](https://www.uvicorn.org/)
* **ORM & Database**: [SQLAlchemy 2.0+](https://www.sqlalchemy.org/) with [SQLite](https://www.sqlite.org/)
* **Data Validation**: [Pydantic v2](https://docs.pydantic.dev/) + `email-validator`
* **Testing**: [Pytest](https://docs.pytest.org/) & [HTTPX](https://www.python-httpx.org/)
* **AI (Optional)**: [Ollama](https://ollama.ai/) (Local LLM inference)

---

## 📋 Prerequisites

Before starting, ensure you have the following installed on your machine:
* **Python 3.10 or higher** ([Download Python](https://www.python.org/downloads/))
* **Git** (Optional, for version control: [Download Git](https://git-scm.com/))

Verify Python is installed:
```bash
python --version
# On macOS/Linux, you might use:
python3 --version
```

---

## 🚀 Installation & Setup

### 1. Clone or Open the Repository
```bash
# If using git:
git clone https://github.com/your-username/student-crud-app.git
cd student-crud-app
```

### 2. Create and Activate a Virtual Environment

* **On Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
  *(If PowerShell scripts are restricted, run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*

* **On Windows (Command Prompt):**
  ```cmd
  python -m venv venv
  venv\Scripts\activate.bat
  ```

* **On macOS / Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 3. Install Project Dependencies
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🏃 Running the Application

Start the local development server with live reload:

```bash
uvicorn app.main:app --reload
```

* **API Base URL**: `http://127.0.0.1:8000`
* **Interactive Swagger UI Docs**: `http://127.0.0.1:8000/docs`
* **Alternative ReDoc Docs**: `http://127.0.0.1:8000/redoc`

---

## 🌱 Seeding the Database

Populate your database with 10 realistic sample student records:

```bash
python seed.py
```

> **Note**: This script is **safe to run multiple times**. It checks existing email addresses and skips duplicates automatically without crashing.

---

## 📚 API Endpoints Reference

| Method | Endpoint | Description | Request Body | Status Codes |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/` | API welcome & health check | *None* | `200` |
| `POST` | `/students` | Register a new student | `StudentCreate` (JSON) | `201`, `409`, `422` |
| `GET` | `/students` | List students with filters & pagination | *Query Parameters* | `200` |
| `GET` | `/students/{id}` | Retrieve a student by their ID | *None* | `200`, `404`, `422` |
| `PUT` | `/students/{id}` | Full update (replaces entire student) | `StudentCreate` (JSON) | `200`, `404`, `409`, `422` |
| `PATCH`| `/students/{id}` | Partial update (updates only sent fields) | `StudentUpdate` (JSON) | `200`, `404`, `409`, `422` |
| `DELETE`| `/students/{id}`| Remove student record permanently | *None* | `204`, `404`, `422` |
| `GET` | `/students/{id}/ai-summary` | Generate AI recommendation via local Ollama | *Query: model* | `200`, `404`, `422` |

---

## 💻 Sample `curl` Commands

### 1. Create a Student (POST)
```bash
curl -X POST "http://127.0.0.1:8000/students" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Alex Mercer",
       "date_of_birth": "2001-08-14",
       "email": "alex.mercer@example.com",
       "phone": "+15559876543",
       "course": "Computer Science",
       "address": "742 Evergreen Terrace",
       "enrollment_date": "2024-01-10"
     }'
```

### 2. List Students with Filters & Pagination (GET)
```bash
curl -X GET "http://127.0.0.1:8000/students?course=Computer&limit=5&skip=0"
```

### 3. Get Student by ID (GET)
```bash
curl -X GET "http://127.0.0.1:8000/students/1"
```

### 4. Full Replacement (PUT)
```bash
curl -X PUT "http://127.0.0.1:8000/students/1" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Alex Mercer Jr.",
       "date_of_birth": "2001-08-14",
       "email": "alex.mercer@example.com",
       "phone": "+15559876543",
       "course": "Software Engineering",
       "address": "800 Technology Way",
       "enrollment_date": "2024-01-10"
     }'
```

### 5. Partial Update (PATCH)
```bash
curl -X PATCH "http://127.0.0.1:8000/students/1" \
     -H "Content-Type: application/json" \
     -d '{
       "course": "Artificial Intelligence"
     }'
```

### 6. Delete a Student (DELETE)
```bash
curl -X DELETE "http://127.0.0.1:8000/students/1" -i
# Returns HTTP/1.1 204 No Content
```

### 7. AI Career & Academic Summary (GET)
```bash
curl -X GET "http://127.0.0.1:8000/students/2/ai-summary"
```

---

## 🧪 Running the Test Suite

The test suite runs using `pytest` against an in-memory SQLite database. **Your physical `students.db` data is never modified by tests.**

Run all tests:
```bash
pytest -v
```

### What the Tests Verify:
* **Creation**: 201 Created and response schema verification.
* **Lookups**: 200 OK retrieval and multi-parameter query filtering (`name`, `course`, `born_after`, `skip`, `limit`).
* **PUT vs PATCH**: Validates full replacement vs partial property modifications.
* **Deletion**: 204 No Content verification and subsequent 404 checks.
* **Conflict (409)**: Duplicate email attempts on POST, PUT, and PATCH.
* **Validation (422)**: Missing contact methods, future date of birth, name length bounds, invalid email formats, and invalid phone numbers.

---

## 🤖 Optional: Local Ollama Setup (AI Feature)

The application includes an optional AI endpoint (`/students/{id}/ai-summary`) powered by a local Large Language Model.

### Setup Instructions:
1. **Install Ollama**: Download from [ollama.ai](https://ollama.ai/).
2. **Download a Model**: Open a terminal and run:
   ```bash
   ollama pull llama3
   ```
   *(You can also use `ollama pull mistral` or `ollama pull phi3`)*
3. **Start Ollama**:
   ```bash
   ollama serve
   ```
4. **Test the Endpoint**:
   Navigate to `/docs` and execute `GET /students/{id}/ai-summary`.

> **Graceful Fallback**: If Ollama is not installed or not running, the API **never crashes with a 500 error**. It returns a clean fallback recommendation advising the student on their course path.

---

## 📂 Project Structure

```text
CRUD/
├── app/
│   ├── __init__.py         # Marks app directory as a Python package
│   ├── ai.py               # Local Ollama AI recommendation helper
│   ├── crud.py             # Database operations & business logic (Create, Read, Update, Delete)
│   ├── database.py         # SQLAlchemy engine, SessionLocal, Base, and get_db dependency
│   ├── main.py             # FastAPI entrypoint, routing, exception handlers
│   ├── models.py           # SQLAlchemy Student database table model
│   └── schemas.py          # Pydantic v2 validation models (StudentCreate, StudentUpdate, StudentOut)
├── tests/
│   ├── __init__.py         # Marks tests directory as a Python package
│   └── test_students.py    # 16 automated pytest unit & integration tests
├── .gitignore              # Ignores venv/, .db files, __pycache__/, and secrets
├── requirements.txt        # Pinned project dependencies
├── seed.py                 # Idempotent database seeder with 10 fake students
└── README.md               # Comprehensive project documentation
```

---

## 📸 Screenshots

*(To add your screenshots, place images inside a `docs/images/` folder and link them below)*

### 1. Interactive Swagger Documentation (`/docs`)
![Swagger UI Documentation](https://raw.githubusercontent.com/swagger-api/swagger-ui/master/flavor/swagger-ui.png)
*(Run `uvicorn app.main:app --reload` and visit `http://127.0.0.1:8000/docs` to see all interactive endpoints).*

### 2. Passing Test Suite Output
```text
tests/test_students.py::test_create_student_success PASSED               [  6%]
tests/test_students.py::test_get_student_by_id_success PASSED            [ 12%]
tests/test_students.py::test_list_students_with_filters_and_pagination PASSED [ 18%]
tests/test_students.py::test_put_student_success PASSED                  [ 25%]
tests/test_students.py::test_patch_student_success PASSED                [ 31%]
tests/test_students.py::test_delete_student_success PASSED               [ 37%]
tests/test_students.py::test_404_on_missing_student_id PASSED            [ 43%]
tests/test_students.py::test_create_duplicate_email_409 PASSED           [ 50%]
tests/test_students.py::test_put_duplicate_email_409 PASSED              [ 56%]
tests/test_students.py::test_patch_duplicate_email_409 PASSED            [ 62%]
tests/test_students.py::test_create_missing_contacts_422 PASSED          [ 68%]
tests/test_students.py::test_create_future_dob_422 PASSED                [ 75%]
tests/test_students.py::test_create_invalid_email_format_422 PASSED      [ 81%]
tests/test_students.py::test_create_invalid_phone_digits_422 PASSED      [ 87%]
tests/test_students.py::test_create_name_too_short_422 PASSED            [ 93%]
tests/test_students.py::test_get_invalid_id_type_422 PASSED              [100%]

======================== 16 passed in 1.91s ========================
```

### 3. Database Seeding Output
```text
============================================================
[START] Starting Student Database Seeding...
============================================================
[INSERTED] ID 1: Alice Johnson (Computer Science)
[INSERTED] ID 2: Bob Smith (Data Science)
...
[COMPLETE] Seeding Complete! Inserted: 10 | Skipped: 0
============================================================
```

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
