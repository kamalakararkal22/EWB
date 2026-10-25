from sqlalchemy import Column, Integer, String, Date, Text
from app.database import Base


class Student(Base):
    """
    SQLAlchemy ORM Model representing the 'students' table in SQLite.
    Each attribute corresponds to a column in the database table.
    """
    __tablename__ = "students"

    # Primary Key: unique identifier for each student record
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Student's full name (required, indexed for faster search)
    name = Column(String(100), nullable=False, index=True)

    # Date of birth (required)
    date_of_birth = Column(Date, nullable=False)

    # Contact details: email and phone are optional in the DB column definition,
    # but application validation ensures at least one is provided upon creation.
    # We set unique=True and index=True so lookups are fast and duplicates are prevented.
    email = Column(String(255), unique=True, index=True, nullable=True)
    phone = Column(String(20), unique=True, index=True, nullable=True)

    # Academic course (e.g. "Computer Science", "Data Science")
    course = Column(String(100), nullable=False, index=True)

    # Residential / contact address (optional)
    address = Column(Text, nullable=True)

    # Date when the student enrolled
    enrollment_date = Column(Date, nullable=False)

    def __repr__(self):
        return f"<Student(id={self.id}, name='{self.name}', course='{self.course}')>"
