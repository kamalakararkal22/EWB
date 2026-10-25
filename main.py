from datetime import date
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status, Query, Path, Response
from sqlalchemy.orm import Session

from app.database import engine, Base, get_db
from app.models import Student
from app.schemas import StudentCreate, StudentUpdate, StudentOut
import app.crud as crud

# Create database tables automatically if they do not exist
Base.metadata.create_all(bind=engine)

# Initialize the FastAPI application
app = FastAPI(
    title="Students Database CRUD Application",
    description="A beginner-friendly REST API for managing student records using FastAPI, SQLAlchemy, and SQLite.",
    version="1.0.0",
)


@app.get("/", tags=["Health Check"])
def root():
    """
    Root endpoint to verify the API is running.
    """
    return {
        "message": "Welcome to the Students Database API!",
        "documentation": "/docs",
    }


@app.post(
    "/students",
    response_model=StudentOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new student",
    tags=["Students"],
    responses={
        201: {"description": "Student created successfully"},
        409: {"description": "Conflict: Duplicate email or phone"},
        422: {"description": "Unprocessable Entity: Validation error in request body"},
    },
)
def create_student_endpoint(
    student_in: StudentCreate,
    db: Session = Depends(get_db),
):
    """
    Add a new student to the database:
    - **name**: 2 to 100 characters (required)
    - **date_of_birth**: Past date in YYYY-MM-DD format (required)
    - **email**: Valid email format (optional, but at least one of email/phone is required)
    - **phone**: 7 to 15 digits (optional, but at least one of email/phone is required)
    - **course**: Name of course/degree (required)
    - **address**: Residential address (optional)
    - **enrollment_date**: Defaults to today if omitted

    Returns **201 Created** on success, **409 Conflict** on duplicate email/phone,
    or **422 Unprocessable Entity** for invalid input.
    """
    return crud.create_student(db=db, student_in=student_in)


@app.get(
    "/students",
    response_model=List[StudentOut],
    status_code=status.HTTP_200_OK,
    summary="List students with filtering and pagination",
    tags=["Students"],
)
def read_students_endpoint(
    name: Optional[str] = Query(
        None,
        description="Filter by student name (case-insensitive partial match)",
    ),
    course: Optional[str] = Query(
        None,
        description="Filter by course (case-insensitive partial match)",
    ),
    born_after: Optional[date] = Query(
        None,
        description="Filter students born strictly after this date (format: YYYY-MM-DD)",
    ),
    skip: int = Query(
        0,
        ge=0,
        description="Number of records to skip (offset for pagination)",
    ),
    limit: int = Query(
        10,
        ge=1,
        le=100,
        description="Maximum number of records to return (1-100)",
    ),
    db: Session = Depends(get_db),
):
    """
    Retrieve all students with optional filters and pagination.
    - **name**: e.g., 'Alice'
    - **course**: e.g., 'Computer Science'
    - **born_after**: e.g., '2000-01-01'
    - **skip**: pagination offset (default: 0)
    - **limit**: pagination count (default: 10, max: 100)
    """
    students = crud.get_students(
        db=db,
        name=name,
        course=course,
        born_after=born_after,
        skip=skip,
        limit=limit,
    )
    return students


@app.get(
    "/students/{id}",
    response_model=StudentOut,
    status_code=status.HTTP_200_OK,
    summary="Get student by ID",
    tags=["Students"],
    responses={
        200: {"description": "Student details retrieved successfully"},
        404: {"description": "Student not found with the given ID"},
        422: {"description": "Invalid student ID parameter"},
    },
)
def read_student_by_id_endpoint(
    id: int = Path(..., ge=1, description="The unique ID of the student to retrieve"),
    db: Session = Depends(get_db),
):
    """
    Retrieve a single student by their unique ID:
    - Returns **200 OK** with student data if found.
    - Returns **404 Not Found** if the student does not exist.
    """
    student = crud.get_student_by_id(db=db, student_id=id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {id} was not found.",
        )
    return student


@app.put(
    "/students/{id}",
    response_model=StudentOut,
    status_code=status.HTTP_200_OK,
    summary="Full update of a student (PUT)",
    tags=["Students"],
    responses={
        200: {"description": "Student completely updated successfully"},
        404: {"description": "Student not found with the given ID"},
        409: {"description": "Conflict: Updated email or phone already belongs to another student"},
        422: {"description": "Validation error in request payload"},
    },
)
def update_student_endpoint(
    id: int = Path(..., ge=1, description="ID of student to replace"),
    student_in: StudentCreate = ...,
    db: Session = Depends(get_db),
):
    """
    Completely replace a student record (PUT):
    - All required student fields must be supplied.
    - Returns **200 OK** with updated student data.
    - Returns **404 Not Found** if ID does not exist.
    - Returns **409 Conflict** if new email/phone is taken by another student.
    """
    return crud.update_student(db=db, student_id=id, student_in=student_in)


@app.patch(
    "/students/{id}",
    response_model=StudentOut,
    status_code=status.HTTP_200_OK,
    summary="Partial update of a student (PATCH)",
    tags=["Students"],
    responses={
        200: {"description": "Student partially updated successfully"},
        404: {"description": "Student not found with the given ID"},
        409: {"description": "Conflict: Updated email or phone already belongs to another student"},
        422: {"description": "Validation error in provided fields"},
    },
)
def patch_student_endpoint(
    id: int = Path(..., ge=1, description="ID of student to update"),
    student_in: StudentUpdate = ...,
    db: Session = Depends(get_db),
):
    """
    Partially update a student record (PATCH):
    - Only send the fields you wish to change.
    - Unsent fields remain completely unchanged.
    - Returns **200 OK** with the modified student.
    - Returns **404 Not Found** if ID does not exist.
    - Returns **409 Conflict** if new email/phone is taken by another student.
    """
    return crud.patch_student(db=db, student_id=id, student_in=student_in)


@app.delete(
    "/students/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a student (DELETE)",
    tags=["Students"],
    responses={
        204: {"description": "Student successfully deleted (no content returned)"},
        404: {"description": "Student not found with the given ID"},
        422: {"description": "Invalid student ID parameter"},
    },
)
def delete_student_endpoint(
    id: int = Path(..., ge=1, description="ID of student to delete"),
    db: Session = Depends(get_db),
):
    """
    Delete a student by ID:
    - Returns **204 No Content** on successful deletion.
    - Returns **404 Not Found** if student does not exist.
    """
    crud.delete_student(db=db, student_id=id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get(
    "/students/{id}/ai-summary",
    summary="Generate AI summary for a student (Optional Ollama)",
    tags=["AI Features"],
    responses={
        200: {"description": "AI recommendation or graceful fallback returned"},
        404: {"description": "Student not found with the given ID"},
        422: {"description": "Invalid student ID parameter"},
    },
)
async def student_ai_summary_endpoint(
    id: int = Path(..., ge=1, description="Student ID"),
    model: str = Query("llama3", description="Ollama model to use (e.g. llama3, mistral)"),
    db: Session = Depends(get_db),
):
    """
    Generate an AI career & academic recommendation for a student using local Ollama.
    Returns graceful fallback guidance if Ollama is not running locally.
    """
    from app.ai import generate_student_summary

    student = crud.get_student_by_id(db=db, student_id=id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {id} was not found.",
        )
    return await generate_student_summary(
        student_name=student.name,
        course=student.course,
        model=model,
    )


