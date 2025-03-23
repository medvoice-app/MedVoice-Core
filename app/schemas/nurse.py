from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional

# Base Nurse schema
class NurseBase(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None

    # Use model_config with ConfigDict
    model_config = ConfigDict(from_attributes=True)

# Schema for nurse creation
class NurseRegister(NurseBase):
    name: str
    email: EmailStr
    password: str

    model_config = ConfigDict(from_attributes=True)

# Schema for nurse update
class NurseUpdate(NurseBase):
    password: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

# Schema for regular nurse response (with strict email validation)
class Nurse(NurseBase):
    id: int
    name: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)

# New schema for nurse response that handles potentially invalid emails
class NurseResponse(BaseModel):
    id: int
    name: str
    email: str  # Using str instead of EmailStr to handle invalid emails in DB

    model_config = ConfigDict(from_attributes=True)

# Schema for nurse login
class NurseLogin(BaseModel):
    email: EmailStr
    password: str

    model_config = ConfigDict(from_attributes=True)
