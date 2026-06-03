from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), default="Student")
    email: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(40), default="student")
    reg_no: Mapped[str | None] = mapped_column(String(60), nullable=True)
    department: Mapped[str | None] = mapped_column(String(100), nullable=True)
    department_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    year: Mapped[str | None] = mapped_column(String(30), nullable=True)
    semester: Mapped[str | None] = mapped_column(String(30), nullable=True)
    current_gpa: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Department(Base):
    __tablename__ = "departments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    degree: Mapped[str] = mapped_column(String(180))
    credits: Mapped[int] = mapped_column(Integer)
    duration: Mapped[str] = mapped_column(String(60))
    medium: Mapped[str | None] = mapped_column(String(60), nullable=True)
    # backref to modules via association table
    modules: Mapped[list["Module"]] = relationship("Module", secondary="module_departments", back_populates="departments")

class Module(Base):
    __tablename__ = "modules"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(180))
    department_code: Mapped[str] = mapped_column(String(20), index=True)
    year: Mapped[str] = mapped_column(String(40))
    semester: Mapped[str] = mapped_column(String(40))
    credits: Mapped[int] = mapped_column(Integer)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # many-to-many to departments (a module can be related to several degree programs)
    departments: Mapped[list["Department"]] = relationship("Department", secondary="module_departments", back_populates="modules")

class Resource(Base):
    __tablename__ = "resources"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(220), index=True)
    module_code: Mapped[str | None] = mapped_column(String(30), nullable=True, index=True)
    department_code: Mapped[str] = mapped_column(String(20), index=True)
    resource_type: Mapped[str] = mapped_column(String(30), index=True)  # ppt, lecture, tutorial, note, pastpaper, video
    file_type: Mapped[str] = mapped_column(String(20), default="PDF")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    downloads: Mapped[int] = mapped_column(Integer, default=0)
    views: Mapped[int] = mapped_column(Integer, default=0)
    is_new: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ModuleDepartment(Base):
    __tablename__ = "module_departments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    module_id: Mapped[int] = mapped_column(Integer, ForeignKey("modules.id"))
    department_id: Mapped[int] = mapped_column(Integer, ForeignKey("departments.id"))


class Enrollment(Base):
    __tablename__ = "enrollments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    module_id: Mapped[int] = mapped_column(ForeignKey("modules.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ForumPost(Base):
    __tablename__ = "forum_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(180))
    body: Mapped[str] = mapped_column(Text)
    module_code: Mapped[str | None] = mapped_column(String(30), nullable=True)
    author_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class ForumReply(Base):
    __tablename__ = "forum_replies"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("forum_posts.id"))
    body: Mapped[str] = mapped_column(Text)
    author_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Notification(Base):
    __tablename__ = "notifications"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(180))
    message: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(40), default="general")
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class SupportMessage(Base):
    __tablename__ = "support_messages"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(160))
    topic: Mapped[str] = mapped_column(String(80))
    message: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), default="open")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class GPACalculation(Base):
    __tablename__ = "gpa_calculations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    gpa: Mapped[float] = mapped_column(Float)
    total_credits: Mapped[float] = mapped_column(Float)
    total_grade_points: Mapped[float] = mapped_column(Float)
    classification: Mapped[str] = mapped_column(String(80))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
