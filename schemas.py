import re
from datetime import date
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator, ConfigDict


# Helper function to validate phone number string
def validate_phone_number(v: Optional[str]) -> Optional[str]:
    if v is None:
        return None
    # Strip common formatting characters: spaces, hyphens, parentheses
    cleaned = re.sub(r"[\s\-\(\)]", "", v)
    # Check if cleaned string matches 7 to 15 digits (optional leading '+')
    if not re.match(r"^\+?[0-9]{7,15}$", cleaned):
        raise ValueError("Phone number must contain between 7 and 15 digits (optional '+' prefix allowed).")
    return cleaned


# Helper function to ensure date of birth is strictly in the past
def validate_dob_in_past(v: Optional[date]) -> Optional[date]:
    if v is not None and v >= date.today():
        raise ValueError("Date of birth must be a date in the past.")
    return v


# Base schema containing shared attributes
class StudentBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Student's full name (2-100 characters)")
    date_of_birth: date = Field(..., description="Date of birth (must be in the past)")
    email: Optional[EmailStr] = Field(None, description="Valid email address")
    phone: Optional[str] = Field(None, description="Phone number containing 7 to 15 digits")
    course: str = Field(..., min_length=1, max_length=100, description="Course or major enrolled in")
    address: Optional[str] = Field(None, description="Residential or postal address")
    enrollment_date: date = Field(default_factory=date.today, description="Date of enrollment")

    @field_validator("date_of_birth")
    @classmethod
    def check_dob(cls, v: date) -> date:
        return validate_dob_in_past(v)

    @field_validator("phone")
    @classmethod
    def check_phone(cls, v: Optional[str]) -> Optional[str]:
        return validate_phone_number(v)

    @field_validator("name", "course")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Field cannot be empty or purely whitespace.")
        return trimmed


# Schema used when creating a new student (POST)
class StudentCreate(StudentBase):
    @model_validator(mode="after")
    def check_at_least_one_contact(self) -> "StudentCreate":
        # Rule: At least one of email or phone must be provided
        if not self.email and not self.phone:
            raise ValueError("At least one contact method (email or phone) is required.")
        return self


# Schema used when updating an existing student (PUT / PATCH)
# All fields are optional so callers can update only specific fields
class StudentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    date_of_birth: Optional[date] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    course: Optional[str] = Field(None, min_length=1, max_length=100)
    address: Optional[str] = None
    enrollment_date: Optional[date] = None

    @field_validator("date_of_birth")
    @classmethod
    def check_dob(cls, v: Optional[date]) -> Optional[date]:
        return validate_dob_in_past(v)

    @field_validator("phone")
    @classmethod
    def check_phone(cls, v: Optional[str]) -> Optional[str]:
        return validate_phone_number(v)

    @field_validator("name", "course")
    @classmethod
    def strip_whitespace(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            trimmed = v.strip()
            if not trimmed:
                raise ValueError("Field cannot be empty or purely whitespace.")
            return trimmed
        return v


# Schema used for returning student data in API responses (GET / POST output)
class StudentOut(BaseModel):
    id: int
    name: str
    date_of_birth: date
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    course: str
    address: Optional[str] = None
    enrollment_date: date

    # Enable ORM mode so Pydantic can read attributes directly from SQLAlchemy model instances
    model_config = ConfigDict(from_attributes=True)
