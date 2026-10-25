from datetime import date
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
# pyrefly: ignore [missing-import]
from fastapi import HTTPException, status

from app.models import Student
from app.schemas import StudentCreate, StudentUpdate


def get_student_by_id(db: Session, student_id: int) -> Optional[Student]:
    """
    Retrieve a single student by their unique primary key ID.
    Returns None if no matching student is found.
    """
    return db.query(Student).filter(Student.id == student_id).first()


def get_student_by_email(db: Session, email: str) -> Optional[Student]:
    """
    Retrieve a student by their email address.
    Used for duplicate check to prevent unique constraint conflicts.
    """
    if not email:
        return None
    return db.query(Student).filter(Student.email == email).first()


def get_student_by_phone(db: Session, phone: str) -> Optional[Student]:
    """
    Retrieve a student by their phone number.
    Used for duplicate check to prevent unique constraint conflicts.
    """
    if not phone:
        return None
    return db.query(Student).filter(Student.phone == phone).first()


def get_students(
    db: Session,
    name: Optional[str] = None,
    course: Optional[str] = None,
    born_after: Optional[date] = None,
    skip: int = 0,
    limit: int = 10,
) -> List[Student]:
    """
    Retrieve a list of students with optional filtering and pagination.
    - name: Case-insensitive partial match
    - course: Case-insensitive partial match
    - born_after: Only students born strictly after this date
    - skip & limit: Pagination offset and count
    """
    query = db.query(Student)

    # Filter by name (case-insensitive search)
    if name:
        query = query.filter(Student.name.ilike(f"%{name}%"))

    # Filter by course (case-insensitive search)
    if course:
        query = query.filter(Student.course.ilike(f"%{course}%"))

    # Filter by date of birth
    if born_after:
        query = query.filter(Student.date_of_birth > born_after)

    # Apply pagination and return the results
    return query.offset(skip).limit(limit).all()


def create_student(db: Session, student_in: StudentCreate) -> Student:
    """
    Create and persist a new student record in the database.
    Performs duplicate checks on email and phone before insertion,
    and safely catches any IntegrityError to avoid unhandled 500 errors.
    """
    # 1. Check if email is already registered
    if student_in.email:
        existing_email = get_student_by_email(db, student_in.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A student with email '{student_in.email}' already exists.",
            )

    # 2. Check if phone is already registered
    if student_in.phone:
        existing_phone = get_student_by_phone(db, student_in.phone)
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A student with phone '{student_in.phone}' already exists.",
            )

    # 3. Create the SQLAlchemy model instance
    db_student = Student(
        name=student_in.name,
        date_of_birth=student_in.date_of_birth,
        email=student_in.email,
        phone=student_in.phone,
        course=student_in.course,
        address=student_in.address,
        enrollment_date=student_in.enrollment_date,
    )

    # 4. Commit to database with error handling
    try:
        db.add(db_student)
        db.commit()
        db.refresh(db_student)
        return db_student
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Database integrity conflict: a student with this unique detail already exists.",
        )


def update_student(
    db: Session,
    student_id: int,
    student_in: StudentCreate,
) -> Student:
    """
    Perform a full replacement (PUT) of a student record.
    Replaces all fields, checks for duplicate email/phone conflicts on other records,
    and returns 404 if the student does not exist.
    """
    db_student = get_student_by_id(db, student_id)
    if not db_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} was not found.",
        )

    # Check if updated email is already taken by a different student
    if student_in.email and student_in.email != db_student.email:
        conflict = (
            db.query(Student)
            .filter(Student.email == student_in.email, Student.id != student_id)
            .first()
        )
        if conflict:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A student with email '{student_in.email}' already exists.",
            )

    # Check if updated phone is already taken by a different student
    if student_in.phone and student_in.phone != db_student.phone:
        conflict = (
            db.query(Student)
            .filter(Student.phone == student_in.phone, Student.id != student_id)
            .first()
        )
        if conflict:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A student with phone '{student_in.phone}' already exists.",
            )

    # Overwrite all fields (full update)
    db_student.name = student_in.name
    db_student.date_of_birth = student_in.date_of_birth
    db_student.email = student_in.email
    db_student.phone = student_in.phone
    db_student.course = student_in.course
    db_student.address = student_in.address
    db_student.enrollment_date = student_in.enrollment_date

    try:
        db.commit()
        db.refresh(db_student)
        return db_student
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Database integrity conflict: a student with this unique detail already exists.",
        )


def patch_student(
    db: Session,
    student_id: int,
    student_in: StudentUpdate,
) -> Student:
    """
    Perform a partial update (PATCH) of a student record.
    Only updates the fields sent in the request payload.
    Checks for conflicts if email or phone are changed.
    """
    db_student = get_student_by_id(db, student_id)
    if not db_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} was not found.",
        )

    # Extract only the fields explicitly supplied in the request body
    update_data = student_in.model_dump(exclude_unset=True)

    # Check duplicate email if email is being updated
    if "email" in update_data and update_data["email"] is not None:
        new_email = update_data["email"]
        if new_email != db_student.email:
            conflict = (
                db.query(Student)
                .filter(Student.email == new_email, Student.id != student_id)
                .first()
            )
            if conflict:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"A student with email '{new_email}' already exists.",
                )

    # Check duplicate phone if phone is being updated
    if "phone" in update_data and update_data["phone"] is not None:
        new_phone = update_data["phone"]
        if new_phone != db_student.phone:
            conflict = (
                db.query(Student)
                .filter(Student.phone == new_phone, Student.id != student_id)
                .first()
            )
            if conflict:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"A student with phone '{new_phone}' already exists.",
                )

    # Validate that after updating, at least one contact method remains
    target_email = update_data.get("email", db_student.email)
    target_phone = update_data.get("phone", db_student.phone)
    if not target_email and not target_phone:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Cannot remove all contact details: at least one of email or phone is required.",
        )

    # Update only the provided attributes
    for field, value in update_data.items():
        setattr(db_student, field, value)

    try:
        db.commit()
        db.refresh(db_student)
        return db_student
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Database integrity conflict: a student with this unique detail already exists.",
        )


def delete_student(db: Session, student_id: int) -> None:
    """
    Delete a student record from the database.
    Raises 404 if the student does not exist.
    """
    db_student = get_student_by_id(db, student_id)
    if not db_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} was not found.",
        )

    db.delete(db_student)
    db.commit()

