from sqlalchemy.orm import Session
from . import models
from .security import hash_password

def seed(db: Session) -> None:
    if db.query(models.User).first():
        return

    admin = models.User(
        name="Admin User",
        email="admin@rajaratakuppi.lk",
        password_hash=hash_password("admin123"),
        role="admin",
        reg_no="ADMIN",
        department="Information Systems",
        department_code="ITM",
        year="Year III",
        semester="Semester I",
        current_gpa=3.45,
    )
    student = models.User(
        name="S. Tharaka",
        email="student@rajaratakuppi.lk",
        password_hash=hash_password("student123"),
        role="student",
        reg_no="2021/MIS/001",
        department="Information Systems",
        department_code="ITM",
        year="Year III",
        semester="Semester I",
        current_gpa=3.45,
    )
    db.add_all([admin, student])

    departments = [
        ("Information Systems", "ITM", "BScHons in Information Systems", 125, "4 Years", "English"),
        ("Accountancy & Finance", "ACF", "BScHons in Accountancy & Finance", 125, "4 Years", "English"),
        ("Business Management", "MGT", "BScHons in Business Management", 124, "4 Years", "English"),
        ("Human Resource Management", "HRM", "BScHons in Human Resource Management", 124, "4 Years", "English"),
        ("Marketing Management", "MKT", "BScHons in Marketing Management", 122, "4 Years", "English"),
        ("Tourism & Hospitality", "THM", "BScHons in Tourism & Hospitality", 125, "4 Years", "English"),
        ("BBA External Degree", "BBA", "General Degree", 90, "3 Years", "Sinhala"),
        ("MBA Programme", "MBA", "Master of Business Administration", 60, "2 Years", "English"),
    ]
    db.add_all([models.Department(name=n, code=c, degree=d, credits=cr, duration=dur, medium=m) for n,c,d,cr,dur,m in departments])

    modules = [
        ("ITM 2133", "Management Information Systems", "ITM", "Year II", "Semester I", 3, "MIS concepts, DSS, ERP systems and organisational impact."),
        ("ITM 2123", "Database Management Systems", "ITM", "Year II", "Semester I", 3, "SQL, ER diagrams, normalization and database design."),
        ("ITM 3133", "Enterprise Architecture", "ITM", "Year III", "Semester I", 3, "SOA, EA frameworks, cloud computing, enterprise data models and IT control."),
        ("ITM 3253", "IS Security & Risk Management", "ITM", "Year III", "Semester II", 3, "Cybersecurity, risk frameworks, access control and incident response."),
        ("ACF 1133", "Financial Accounting", "ACF", "Year I", "Semester I", 3, "Journal entries, trial balance and financial statements."),
        ("ACF 2224", "Financial Management", "ACF", "Year II", "Semester II", 4, "Capital budgeting, working capital and valuation."),
        ("ACF 3113", "Investment & Portfolio Management", "ACF", "Year III", "Semester I", 3, "Portfolio theory, risk-return trade-off and asset pricing."),
        ("HRM 3113", "Employment Law & Industrial Relations", "HRM", "Year III", "Semester I", 3, "Sri Lanka labour law, trade unions and industrial disputes."),
        ("MGT 1113", "Principles of Management", "MGT", "Year I", "Semester I", 3, "Planning, organising, leading and controlling."),
        ("MGT 3243", "Strategic Management", "MGT", "Year III", "Semester II", 3, "SWOT, Five Forces, balanced scorecard and implementation."),
        ("MKT 2123", "Digital Marketing", "MKT", "Year II", "Semester I", 3, "SEO, SEM, social media marketing, content strategy and analytics."),
        ("THM 11023", "Introduction to Tourism & Hospitality", "THM", "Year I", "Semester I", 3, "Tourism types, hospitality sectors and Sri Lanka tourism overview."),
    ]
    db.add_all([models.Module(code=c, title=t, department_code=d, year=y, semester=s, credits=cr, description=desc) for c,t,d,y,s,cr,desc in modules])

    resources = [
        ("ITM 3133 — Enterprise Architecture Notes", "ITM 3133", "ITM", "lecture", "PDF", "SOA, EA frameworks, cloud computing, enterprise data models and IT control.", 312, 900, True),
        ("ACF 3113 — Investment & Portfolio Management", "ACF 3113", "ACF", "lecture", "DOC", "Investment vehicles, portfolio theory, risk-return trade-off and asset pricing.", 267, 720, False),
        ("HRM 3113 — Employment Law Slides", "HRM 3113", "HRM", "ppt", "PPT", "Sri Lanka labour law, trade unions and industrial disputes slides.", 198, 600, False),
        ("MGT 1113 — Principles of Management Quick Notes", "MGT 1113", "MGT", "note", "PDF", "POLC framework and management thought quick reference.", 1200, 2400, False),
        ("ITM 2123 — DBMS Tutorial", "ITM 2123", "ITM", "tutorial", "PDF", "SQL queries, ER diagrams, normalisation exercises and answers.", 430, 1100, True),
        ("ACF 1133 — Financial Accounting Tutorial", "ACF 1133", "ACF", "tutorial", "PDF", "Journal entries, trial balance and statements worked examples.", 510, 1400, False),
        ("MKT 2123 — Digital Marketing Slides", "MKT 2123", "MKT", "ppt", "PPT", "SEO, SEM, social media marketing and analytics slides.", 260, 890, False),
        ("ITM 2024 Final Past Paper", "ITM 2133", "ITM", "pastpaper", "PDF", "Final examination paper with common question patterns.", 645, 0, True),
        ("ACF 2023 Past Paper", "ACF 2224", "ACF", "pastpaper", "PDF", "Financial management past paper for revision.", 480, 0, False),
    ]
    db.add_all([models.Resource(title=t, module_code=m, department_code=d, resource_type=rt, file_type=ft, description=desc, downloads=dl, views=v, is_new=n) for t,m,d,rt,ft,desc,dl,v,n in resources])

    db.add_all([
        models.Notification(title="New IS Security Notes Added", message="ITM 3253 notes are now available in Student Material.", category="materials", is_read=False),
        models.Notification(title="GPA Calculator Updated", message="The GPA calculator now supports saving calculation history.", category="tools", is_read=False),
        models.Notification(title="Past Papers Uploaded", message="New ITM and ACF past papers were added today.", category="pastpapers", is_read=False),
    ])

    db.add_all([
        models.ForumPost(title="How to prepare for ITM 2123 DBMS?", body="Share your tips for SQL and ER diagram questions.", module_code="ITM 2123", author_id=2),
        models.ForumPost(title="ACF 2224 capital budgeting help", body="Can someone explain NPV vs IRR using a simple example?", module_code="ACF 2224", author_id=2),
    ])
    db.commit()
