from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from ..security import get_current_user

router = APIRouter(prefix="/gpa", tags=["GPA"])

grade_map = {
    "A+": 4.0, "A": 4.0, "A-": 3.7, "B+": 3.3, "B": 3.0, "B-": 2.7,
    "C+": 2.3, "C": 2.0, "C-": 1.7, "D": 1.0, "E": 0.0
}

def classify(gpa: float) -> str:
    if gpa >= 3.70: return "First Class Honours"
    if gpa >= 3.30: return "Second Class Upper Division"
    if gpa >= 2.70: return "Second Class Lower Division"
    if gpa >= 2.00: return "Pass"
    return "Fail / Requires Improvement"

@router.get("/grades")
def grade_scale():
    return grade_map

@router.post("/calculate", response_model=schemas.GPAResponse)
def calculate(payload: schemas.GPARequest, db: Session = Depends(get_db), user: models.User | None = Depends(get_current_user)):
    if not payload.rows:
        raise HTTPException(status_code=400, detail="At least one module row is required")
    total_credits = 0.0
    total_grade_points = 0.0
    for row in payload.rows:
        grade = row.grade.upper()
        if grade not in grade_map:
            raise HTTPException(status_code=400, detail=f"Invalid grade: {row.grade}")
        total_credits += row.credits
        total_grade_points += row.credits * grade_map[grade]
    gpa = round(total_grade_points / total_credits, 2)
    result = schemas.GPAResponse(gpa=gpa, total_credits=total_credits, total_grade_points=round(total_grade_points, 2), classification=classify(gpa))
    db.add(models.GPACalculation(user_id=user.id if user else None, **result.model_dump()))
    if user:
        user.current_gpa = gpa
    db.commit()
    return result

@router.get("/history")
def history(db: Session = Depends(get_db), user: models.User | None = Depends(get_current_user)):
    q = db.query(models.GPACalculation)
    if user:
        q = q.filter(models.GPACalculation.user_id == user.id)
    return q.order_by(models.GPACalculation.created_at.desc()).limit(20).all()
