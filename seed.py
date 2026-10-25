"""
seed.py - Database Seeding Script

This script populates the SQLite database with 10 realistic sample student records.
It is designed to be idempotent (safe to run multiple times):
- Before inserting, it checks whether each student's email already exists.
- Existing records are safely skipped without throwing errors or causing duplicate conflicts.
"""

from datetime import date
from app.database import engine, Base, SessionLocal
from app.models import Student

# Ensure database tables exist before seeding
Base.metadata.create_all(bind=engine)

# 10 realistic fake student records
FAKE_STUDENTS = [
    {
        "name": "Alice Johnson",
        "date_of_birth": date(2001, 3, 15),
        "email": "alice.johnson@example.com",
        "phone": "+15551234501",
        "course": "Computer Science",
        "address": "101 Campus Way, Seattle, WA",
        "enrollment_date": date(2023, 9, 1),
    },
    {
        "name": "Bob Smith",
        "date_of_birth": date(2002, 7, 22),
        "email": "bob.smith@example.com",
        "phone": "+15551234502",
        "course": "Data Science",
        "address": "204 Oak St, Portland, OR",
        "enrollment_date": date(2023, 9, 1),
    },
    {
        "name": "Charlie Brown",
        "date_of_birth": date(2000, 11, 5),
        "email": "charlie.brown@example.com",
        "phone": "+15551234503",
        "course": "Mechanical Engineering",
        "address": "309 Pine Rd, Austin, TX",
        "enrollment_date": date(2022, 9, 1),
    },
    {
        "name": "Diana Prince",
        "date_of_birth": date(2001, 9, 18),
        "email": "diana.prince@example.com",
        "phone": "+15551234504",
        "course": "Cybersecurity",
        "address": "412 Maple Ave, Chicago, IL",
        "enrollment_date": date(2023, 9, 1),
    },
    {
        "name": "Evan Wright",
        "date_of_birth": date(2003, 1, 30),
        "email": "evan.wright@example.com",
        "phone": "+15551234505",
        "course": "Computer Science",
        "address": "520 Cedar Blvd, Boston, MA",
        "enrollment_date": date(2024, 1, 15),
    },
    {
        "name": "Fiona Gallagher",
        "date_of_birth": date(1999, 12, 12),
        "email": "fiona.gallagher@example.com",
        "phone": "+15551234506",
        "course": "Business Administration",
        "address": "633 Elm Dr, Denver, CO",
        "enrollment_date": date(2022, 1, 15),
    },
    {
        "name": "George Clark",
        "date_of_birth": date(2002, 4, 8),
        "email": "george.clark@example.com",
        "phone": "+15551234507",
        "course": "Mathematics",
        "address": "744 Birch Ln, San Francisco, CA",
        "enrollment_date": date(2023, 9, 1),
    },
    {
        "name": "Hannah Abbott",
        "date_of_birth": date(2001, 6, 25),
        "email": "hannah.abbott@example.com",
        "phone": "+15551234508",
        "course": "Data Science",
        "address": "855 Walnut Ct, New York, NY",
        "enrollment_date": date(2023, 9, 1),
    },
    {
        "name": "Ian Malcolm",
        "date_of_birth": date(2000, 8, 14),
        "email": "ian.malcolm@example.com",
        "phone": "+15551234509",
        "course": "Physics",
        "address": "966 Spruce Pl, Atlanta, GA",
        "enrollment_date": date(2022, 9, 1),
    },
    {
        "name": "Julia Roberts",
        "date_of_birth": date(2002, 10, 3),
        "email": "julia.roberts@example.com",
        "phone": "+15551234510",
        "course": "Software Engineering",
        "address": "1077 Willow Way, San Diego, CA",
        "enrollment_date": date(2024, 1, 15),
    },
]


def seed_database():
    """
    Connects to SQLite, checks for existing emails, and inserts missing students.
    """
    db = SessionLocal()
    inserted_count = 0
    skipped_count = 0

    print("=" * 60)
    print("[START] Starting Student Database Seeding...")
    print("=" * 60)

    try:
        for student_data in FAKE_STUDENTS:
            email = student_data["email"]

            # Check if this student already exists by email
            existing = db.query(Student).filter(Student.email == email).first()

            if existing:
                print(f"[SKIPPED] {student_data['name']} (email: '{email}' already exists)")
                skipped_count += 1
            else:
                new_student = Student(**student_data)
                db.add(new_student)
                db.commit()
                db.refresh(new_student)
                print(f"[INSERTED] ID {new_student.id}: {new_student.name} ({new_student.course})")
                inserted_count += 1

        print("=" * 60)
        print(f"[COMPLETE] Seeding Complete! Inserted: {inserted_count} | Skipped: {skipped_count}")
        print("=" * 60)

    except Exception as e:
        db.rollback()
        print(f"❌ Error occurred during seeding: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
