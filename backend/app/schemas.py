from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=6)
    reg_no: str | None = None
    department: str | None = None
    department_code: str | None = None
    year: str | None = None
    semester: str | None = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    reg_no: str | None = None
    department: str | None = None
    department_code: str | None = None
    year: str | None = None
    semester: str | None = None
    current_gpa: float | None = None
    class Config: from_attributes = True

class UserUpdate(BaseModel):
    name: str | None = None
    reg_no: str | None = None
    department: str | None = None
    department_code: str | None = None
    year: str | None = None
    semester: str | None = None
    current_gpa: float | None = None

class DepartmentOut(BaseModel):
    id: int
    name: str
    code: str
    degree: str
    credits: int
    duration: str
    medium: str | None = None
    class Config: from_attributes = True

class ModuleCreate(BaseModel):
    code: str
    title: str
    department_code: str
    year: str
    semester: str
    credits: int
    description: str | None = None
    # list of department codes this module relates to (optional)
    departments: list[str] | None = None

class ModuleOut(BaseModel):
    id: int
    code: str
    title: str
    year: str
    semester: str
    credits: int
    description: str | None = None
    department_code: str
    departments: list[DepartmentOut] | None = None
    class Config: from_attributes = True

class EnrollmentOut(BaseModel):
    id: int
    user_id: int | None = None
    module_id: int
    created_at: datetime
    class Config: from_attributes = True

class ResourceCreate(BaseModel):
    title: str
    module_code: str | None = None
    department_code: str
    resource_type: str
    file_type: str = "PDF"
    description: str | None = None
    file_url: str | None = None
    is_new: bool = False

class ResourceOut(ResourceCreate):
    id: int
    downloads: int
    views: int
    created_at: datetime
    class Config: from_attributes = True

class ForumPostCreate(BaseModel):
    title: str
    body: str
    module_code: str | None = None

class ForumPostOut(ForumPostCreate):
    id: int
    author_id: int | None = None
    created_at: datetime
    class Config: from_attributes = True

class ReplyCreate(BaseModel):
    body: str

class ReplyOut(ReplyCreate):
    id: int
    post_id: int
    author_id: int | None = None
    created_at: datetime
    class Config: from_attributes = True

class NotificationCreate(BaseModel):
    title: str
    message: str
    category: str = "general"

class NotificationOut(NotificationCreate):
    id: int
    is_read: bool
    created_at: datetime
    class Config: from_attributes = True

class SupportMessageCreate(BaseModel):
    name: str
    email: EmailStr
    topic: str
    message: str

class SupportMessageOut(SupportMessageCreate):
    id: int
    status: str
    created_at: datetime
    class Config: from_attributes = True

class GPARow(BaseModel):
    module: str | None = None
    credits: float = Field(gt=0)
    grade: str

class GPARequest(BaseModel):
    rows: list[GPARow]

class GPAResponse(BaseModel):
    gpa: float
    total_credits: float
    total_grade_points: float
    classification: str
