"""
tests/test_students.py

Automated test suite using pytest and FastAPI's TestClient.
Uses an isolated in-memory SQLite database via FastAPI's `dependency_overrides`
to ensure tests never touch or modify the production database file.
"""

import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db

# 1. Setup an in-memory SQLite database for testing
# StaticPool ensures the in-memory SQLite database connection remains open and shared
# across all operations within each test function.
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


@pytest.fixture(scope="function")
def client():
    """
    Pytest fixture that:
    1. Creates all tables in the temporary in-memory database.
    2. Overrides the `get_db` FastAPI dependency so route handlers query this test DB.
    3. Yields the TestClient to the test function.
    4. Cleans up tables and removes dependency overrides after each test.
    """
    # Create fresh schema in the temporary database
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    # Apply FastAPI dependency override
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # Teardown: clear override and drop all temporary tables
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)


# Helper dictionary for creating sample students
SAMPLE_STUDENT_1 = {
    "name": "Harry Potter",
    "date_of_birth": "2000-07-31",
    "email": "harry.potter@example.com",
    "phone": "+1234567890",
    "course": "Defense Against Dark Arts",
    "address": "4 Privet Drive",
    "enrollment_date": "2023-09-01",
}

SAMPLE_STUDENT_2 = {
    "name": "Hermione Granger",
    "date_of_birth": "1999-09-19",
    "email": "hermione.granger@example.com",
    "phone": "+1987654321",
    "course": "Arithmancy",
    "address": "12 Grimmauld Place",
    "enrollment_date": "2023-09-01",
}


# ============================================================================
# 1. CREATE (POST) TESTS
# ============================================================================

def test_create_student_success(client):
    """Test creating a student successfully returns 201 Created and correct body."""
    response = client.post("/students", json=SAMPLE_STUDENT_1)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == SAMPLE_STUDENT_1["name"]
    assert data["email"] == SAMPLE_STUDENT_1["email"]
    assert data["phone"] == SAMPLE_STUDENT_1["phone"]
    assert data["course"] == SAMPLE_STUDENT_1["course"]


# ============================================================================
# 2. GET (BY ID & LIST WITH FILTERS / PAGINATION) TESTS
# ============================================================================

def test_get_student_by_id_success(client):
    """Test retrieving an existing student by ID returns 200 OK."""
    create_res = client.post("/students", json=SAMPLE_STUDENT_1)
    student_id = create_res.json()["id"]

    response = client.get(f"/students/{student_id}")
    assert response.status_code == 200
    assert response.json()["name"] == SAMPLE_STUDENT_1["name"]


def test_list_students_with_filters_and_pagination(client):
    """Test list filtering by name, course, born_after, and pagination (skip/limit)."""
    # Create two distinct students
    client.post("/students", json=SAMPLE_STUDENT_1)
    client.post("/students", json=SAMPLE_STUDENT_2)

    # Filter by name partial match
    res_name = client.get("/students?name=Harry")
    assert res_name.status_code == 200
    data_name = res_name.json()
    assert len(data_name) == 1
    assert data_name[0]["name"] == "Harry Potter"

    # Filter by course
    res_course = client.get("/students?course=Arithmancy")
    assert res_course.status_code == 200
    assert len(res_course.json()) == 1
    assert res_course.json()[0]["name"] == "Hermione Granger"

    # Filter by born_after
    res_dob = client.get("/students?born_after=2000-01-01")
    assert res_dob.status_code == 200
    assert len(res_dob.json()) == 1
    assert res_dob.json()[0]["name"] == "Harry Potter"

    # Test pagination: limit=1, skip=1
    res_paged = client.get("/students?limit=1&skip=1")
    assert res_paged.status_code == 200
    assert len(res_paged.json()) == 1


# ============================================================================
# 3. PUT (FULL UPDATE) TESTS
# ============================================================================

def test_put_student_success(client):
    """Test full update with PUT completely updates all student fields."""
    create_res = client.post("/students", json=SAMPLE_STUDENT_1)
    student_id = create_res.json()["id"]

    updated_payload = {
        "name": "Harry James Potter",
        "date_of_birth": "2000-07-31",
        "email": "harry.auror@example.com",
        "phone": "+1234567890",
        "course": "Auror Training",
        "address": "Ministry of Magic",
        "enrollment_date": "2024-01-01",
    }
    response = client.put(f"/students/{student_id}", json=updated_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Harry James Potter"
    assert data["email"] == "harry.auror@example.com"
    assert data["course"] == "Auror Training"


# ============================================================================
# 4. PATCH (PARTIAL UPDATE) TESTS
# ============================================================================

def test_patch_student_success(client):
    """Test PATCH only modifies the fields sent in the request."""
    create_res = client.post("/students", json=SAMPLE_STUDENT_1)
    student_id = create_res.json()["id"]

    patch_payload = {"course": "Advanced Potions"}
    response = client.patch(f"/students/{student_id}", json=patch_payload)
    assert response.status_code == 200
    data = response.json()
    # Updated field
    assert data["course"] == "Advanced Potions"
    # Unchanged fields remain intact
    assert data["name"] == SAMPLE_STUDENT_1["name"]
    assert data["email"] == SAMPLE_STUDENT_1["email"]
    assert data["phone"] == SAMPLE_STUDENT_1["phone"]


# ============================================================================
# 5. DELETE TESTS
# ============================================================================

def test_delete_student_success(client):
    """Test DELETE removes student, returns 204 No Content, and student is gone."""
    create_res = client.post("/students", json=SAMPLE_STUDENT_1)
    student_id = create_res.json()["id"]

    del_res = client.delete(f"/students/{student_id}")
    assert del_res.status_code == 204
    assert del_res.content == b""  # 204 must return empty body

    # Verify student no longer exists
    get_res = client.get(f"/students/{student_id}")
    assert get_res.status_code == 404


# ============================================================================
# 6. 404 NOT FOUND TESTS
# ============================================================================

def test_404_on_missing_student_id(client):
    """Verify GET, PUT, PATCH, and DELETE all return 404 when ID does not exist."""
    missing_id = 99999

    # GET missing ID
    assert client.get(f"/students/{missing_id}").status_code == 404

    # PUT missing ID
    assert client.put(f"/students/{missing_id}", json=SAMPLE_STUDENT_1).status_code == 404

    # PATCH missing ID
    assert client.patch(f"/students/{missing_id}", json={"course": "CS"}).status_code == 404

    # DELETE missing ID
    assert client.delete(f"/students/{missing_id}").status_code == 404


# ============================================================================
# 7. 409 CONFLICT TESTS (DUPLICATE EMAIL)
# ============================================================================

def test_create_duplicate_email_409(client):
    """Test creating two students with identical emails triggers 409 Conflict."""
    client.post("/students", json=SAMPLE_STUDENT_1)
    duplicate_res = client.post("/students", json=SAMPLE_STUDENT_1)
    assert duplicate_res.status_code == 409
    assert "already exists" in duplicate_res.json()["detail"]


def test_put_duplicate_email_409(client):
    """Test PUT changing email to an email owned by another student returns 409."""
    client.post("/students", json=SAMPLE_STUDENT_1)
    res2 = client.post("/students", json=SAMPLE_STUDENT_2)
    student2_id = res2.json()["id"]

    # Attempt to update student 2 to use student 1's email
    conflict_payload = {**SAMPLE_STUDENT_2, "email": SAMPLE_STUDENT_1["email"]}
    put_res = client.put(f"/students/{student2_id}", json=conflict_payload)
    assert put_res.status_code == 409


def test_patch_duplicate_email_409(client):
    """Test PATCH updating email to another student's email returns 409."""
    client.post("/students", json=SAMPLE_STUDENT_1)
    res2 = client.post("/students", json=SAMPLE_STUDENT_2)
    student2_id = res2.json()["id"]

    patch_res = client.patch(f"/students/{student2_id}", json={"email": SAMPLE_STUDENT_1["email"]})
    assert patch_res.status_code == 409


# ============================================================================
# 8. 422 UNPROCESSABLE ENTITY TESTS (INPUT VALIDATION)
# ============================================================================

def test_create_missing_contacts_422(client):
    """Test creating student with neither email nor phone returns 422."""
    bad_payload = {
        "name": "No Contact Student",
        "date_of_birth": "2000-01-01",
        "course": "Art",
    }
    response = client.post("/students", json=bad_payload)
    assert response.status_code == 422


def test_create_future_dob_422(client):
    """Test student with future date of birth fails with 422."""
    bad_payload = {
        **SAMPLE_STUDENT_1,
        "date_of_birth": "2099-01-01",
    }
    response = client.post("/students", json=bad_payload)
    assert response.status_code == 422


def test_create_invalid_email_format_422(client):
    """Test student with ill-formatted email returns 422."""
    bad_payload = {
        **SAMPLE_STUDENT_1,
        "email": "not-a-valid-email",
    }
    response = client.post("/students", json=bad_payload)
    assert response.status_code == 422


def test_create_invalid_phone_digits_422(client):
    """Test phone with fewer than 7 digits returns 422."""
    bad_payload = {
        **SAMPLE_STUDENT_1,
        "phone": "12345",  # only 5 digits
    }
    response = client.post("/students", json=bad_payload)
    assert response.status_code == 422


def test_create_name_too_short_422(client):
    """Test name with only 1 character (<2 min_length) returns 422."""
    bad_payload = {
        **SAMPLE_STUDENT_1,
        "name": "H",
    }
    response = client.post("/students", json=bad_payload)
    assert response.status_code == 422


def test_get_invalid_id_type_422(client):
    """Test passing non-integer ID into route returns 422."""
    response = client.get("/students/not-an-int")
    assert response.status_code == 422
