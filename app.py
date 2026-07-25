import os
from datetime import date, datetime
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin, login_user, logout_user,
    login_required, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-this-secret-key")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "school.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Simple API key for mobile / external API access (change this!)
API_KEY = os.environ.get("SCHOOL_API_KEY", "mojidpur-secret-key-2026")

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Please log in."


# ----------------------- MODELS -----------------------

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="admin")  # admin / teacher

    def set_password(self, pw):
        self.password_hash = generate_password_hash(pw)

    def check_password(self, pw):
        return check_password_hash(self.password_hash, pw)


class Institute(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), default="Mojidpur Central School")
    address = db.Column(db.String(300), default="")
    phone = db.Column(db.String(50), default="")
    email = db.Column(db.String(120), default="")
    institute_id = db.Column(db.String(50), default="92387")
    academic_year = db.Column(db.String(10), default="2026")


class SchoolClass(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)  # e.g. "Class 5"
    sections = db.relationship("Section", backref="school_class", cascade="all, delete-orphan")


class Section(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)  # e.g. "A"
    class_id = db.Column(db.Integer, db.ForeignKey("school_class.id"), nullable=False)


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    roll = db.Column(db.String(20))
    class_id = db.Column(db.Integer, db.ForeignKey("school_class.id"))
    section_id = db.Column(db.Integer, db.ForeignKey("section.id"))
    father_name = db.Column(db.String(120))
    mother_name = db.Column(db.String(120))
    phone = db.Column(db.String(50))
    address = db.Column(db.String(300))
    admission_date = db.Column(db.String(20))
    photo = db.Column(db.String(200))

    school_class = db.relationship("SchoolClass")
    section = db.relationship("Section")


class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    designation = db.Column(db.String(120))
    phone = db.Column(db.String(50))
    email = db.Column(db.String(120))
    address = db.Column(db.String(300))
    joining_date = db.Column(db.String(20))
    photo = db.Column(db.String(200))


class StudentAttendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default="Present")  # Present/Absent/Leave
    student = db.relationship("Student")
    __table_args__ = (db.UniqueConstraint("student_id", "date", name="uq_student_date"),)


class TeacherAttendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey("teacher.id"), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default="Present")
    teacher = db.relationship("Teacher")
    __table_args__ = (db.UniqueConstraint("teacher_id", "date", name="uq_teacher_date"),)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ----------------------- HELPERS -----------------------

def api_key_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        key = request.headers.get("X-API-KEY") or request.args.get("api_key")
        if key != API_KEY:
            return jsonify({"error": "Invalid or missing API key"}), 401
        return f(*args, **kwargs)
    return wrapper


def save_photo(file_storage):
    if file_storage and file_storage.filename:
        filename = secure_filename(file_storage.filename)
        unique = f"{datetime.utcnow().timestamp()}_{filename}"
        path = os.path.join(app.config["UPLOAD_FOLDER"], unique)
        file_storage.save(path)
        return unique
    return None


# ----------------------- AUTH ROUTES -----------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("dashboard"))
        flash("Invalid username or password!", "danger")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


# ----------------------- DASHBOARD -----------------------

@app.route("/")
@login_required
def dashboard():
    inst = Institute.query.first()
    total_students = Student.query.count()
    total_teachers = Teacher.query.count()
    total_classes = SchoolClass.query.count()
    today = date.today().isoformat()
    present_today = StudentAttendance.query.filter_by(date=today, status="Present").count()
    return render_template(
        "dashboard.html", inst=inst,
        total_students=total_students, total_teachers=total_teachers,
        total_classes=total_classes, present_today=present_today, today=today
    )


# ----------------------- STUDENTS (WEB) -----------------------

@app.route("/students")
@login_required
def students():
    class_id = request.args.get("class_id", type=int)
    q = Student.query
    if class_id:
        q = q.filter_by(class_id=class_id)
    all_students = q.order_by(Student.name).all()
    classes = SchoolClass.query.all()
    return render_template("students.html", students=all_students, classes=classes, selected_class=class_id)


@app.route("/students/add", methods=["GET", "POST"])
@login_required
def add_student():
    classes = SchoolClass.query.all()
    if request.method == "POST":
        photo_file = save_photo(request.files.get("photo"))
        s = Student(
            name=request.form["name"],
            roll=request.form.get("roll"),
            class_id=request.form.get("class_id", type=int),
            section_id=request.form.get("section_id", type=int) or None,
            father_name=request.form.get("father_name"),
            mother_name=request.form.get("mother_name"),
            phone=request.form.get("phone"),
            address=request.form.get("address"),
            admission_date=request.form.get("admission_date"),
            photo=photo_file,
        )
        db.session.add(s)
        db.session.commit()
        flash("Student added successfully!", "success")
        return redirect(url_for("students"))
    return render_template("student_form.html", classes=classes, student=None)


@app.route("/students/<int:student_id>/edit", methods=["GET", "POST"])
@login_required
def edit_student(student_id):
    s = Student.query.get_or_404(student_id)
    classes = SchoolClass.query.all()
    if request.method == "POST":
        s.name = request.form["name"]
        s.roll = request.form.get("roll")
        s.class_id = request.form.get("class_id", type=int)
        s.section_id = request.form.get("section_id", type=int) or None
        s.father_name = request.form.get("father_name")
        s.mother_name = request.form.get("mother_name")
        s.phone = request.form.get("phone")
        s.address = request.form.get("address")
        s.admission_date = request.form.get("admission_date")
        photo_file = save_photo(request.files.get("photo"))
        if photo_file:
            s.photo = photo_file
        db.session.commit()
        flash("Information updated successfully!", "success")
        return redirect(url_for("students"))
    return render_template("student_form.html", classes=classes, student=s)


@app.route("/students/<int:student_id>/delete", methods=["POST"])
@login_required
def delete_student(student_id):
    s = Student.query.get_or_404(student_id)
    db.session.delete(s)
    db.session.commit()
    flash("Student deleted successfully!", "info")
    return redirect(url_for("students"))


# ----------------------- TEACHERS (WEB) -----------------------

@app.route("/teachers")
@login_required
def teachers():
    all_teachers = Teacher.query.order_by(Teacher.name).all()
    return render_template("teachers.html", teachers=all_teachers)


@app.route("/teachers/add", methods=["GET", "POST"])
@login_required
def add_teacher():
    if request.method == "POST":
        photo_file = save_photo(request.files.get("photo"))
        t = Teacher(
            name=request.form["name"],
            designation=request.form.get("designation"),
            phone=request.form.get("phone"),
            email=request.form.get("email"),
            address=request.form.get("address"),
            joining_date=request.form.get("joining_date"),
            photo=photo_file,
        )
        db.session.add(t)
        db.session.commit()
        flash("Teacher added successfully!", "success")
        return redirect(url_for("teachers"))
    return render_template("teacher_form.html", teacher=None)


@app.route("/teachers/<int:teacher_id>/edit", methods=["GET", "POST"])
@login_required
def edit_teacher(teacher_id):
    t = Teacher.query.get_or_404(teacher_id)
    if request.method == "POST":
        t.name = request.form["name"]
        t.designation = request.form.get("designation")
        t.phone = request.form.get("phone")
        t.email = request.form.get("email")
        t.address = request.form.get("address")
        t.joining_date = request.form.get("joining_date")
        photo_file = save_photo(request.files.get("photo"))
        if photo_file:
            t.photo = photo_file
        db.session.commit()
        flash("Information updated successfully!", "success")
        return redirect(url_for("teachers"))
    return render_template("teacher_form.html", teacher=t)


@app.route("/teachers/<int:teacher_id>/delete", methods=["POST"])
@login_required
def delete_teacher(teacher_id):
    t = Teacher.query.get_or_404(teacher_id)
    db.session.delete(t)
    db.session.commit()
    flash("Teacher deleted successfully!", "info")
    return redirect(url_for("teachers"))


# ----------------------- CLASSES / SECTIONS (WEB) -----------------------

@app.route("/classes", methods=["GET", "POST"])
@login_required
def classes():
    if request.method == "POST":
        name = request.form.get("class_name", "").strip()
        if name:
            db.session.add(SchoolClass(name=name))
            db.session.commit()
            flash("Class added successfully!", "success")
        return redirect(url_for("classes"))
    all_classes = SchoolClass.query.all()
    return render_template("classes.html", classes=all_classes)


@app.route("/classes/<int:class_id>/add_section", methods=["POST"])
@login_required
def add_section(class_id):
    name = request.form.get("section_name", "").strip()
    if name:
        db.session.add(Section(name=name, class_id=class_id))
        db.session.commit()
        flash("Section added successfully!", "success")
    return redirect(url_for("classes"))


@app.route("/api/sections/<int:class_id>")
@login_required
def sections_by_class(class_id):
    secs = Section.query.filter_by(class_id=class_id).all()
    return jsonify([{"id": s.id, "name": s.name} for s in secs])


# ----------------------- STUDENT ATTENDANCE (WEB) -----------------------

@app.route("/attendance/students", methods=["GET", "POST"])
@login_required
def attendance_students():
    classes = SchoolClass.query.all()
    class_id = request.args.get("class_id", type=int) or request.form.get("class_id", type=int)
    att_date = request.args.get("date") or request.form.get("date") or date.today().isoformat()

    if request.method == "POST":
        student_ids = request.form.getlist("student_id")
        for sid in student_ids:
            status = request.form.get(f"status_{sid}", "Present")
            existing = StudentAttendance.query.filter_by(student_id=int(sid), date=att_date).first()
            if existing:
                existing.status = status
            else:
                db.session.add(StudentAttendance(student_id=int(sid), date=att_date, status=status))
        db.session.commit()
        flash("Attendance saved successfully!", "success")
        return redirect(url_for("attendance_students", class_id=class_id, date=att_date))

    students_list = []
    if class_id:
        students_list = Student.query.filter_by(class_id=class_id).order_by(Student.roll).all()
        existing_att = {a.student_id: a.status for a in StudentAttendance.query.filter_by(date=att_date).all()}
        for s in students_list:
            s.current_status = existing_att.get(s.id, "Present")

    return render_template(
        "attendance_student.html", classes=classes, students=students_list,
        selected_class=class_id, att_date=att_date
    )


# ----------------------- TEACHER ATTENDANCE (WEB) -----------------------

@app.route("/attendance/teachers", methods=["GET", "POST"])
@login_required
def attendance_teachers():
    att_date = request.args.get("date") or request.form.get("date") or date.today().isoformat()

    if request.method == "POST":
        teacher_ids = request.form.getlist("teacher_id")
        for tid in teacher_ids:
            status = request.form.get(f"status_{tid}", "Present")
            existing = TeacherAttendance.query.filter_by(teacher_id=int(tid), date=att_date).first()
            if existing:
                existing.status = status
            else:
                db.session.add(TeacherAttendance(teacher_id=int(tid), date=att_date, status=status))
        db.session.commit()
        flash("Attendance saved successfully!", "success")
        return redirect(url_for("attendance_teachers", date=att_date))

    all_teachers = Teacher.query.order_by(Teacher.name).all()
    existing_att = {a.teacher_id: a.status for a in TeacherAttendance.query.filter_by(date=att_date).all()}
    for t in all_teachers:
        t.current_status = existing_att.get(t.id, "Present")

    return render_template("attendance_teacher.html", teachers=all_teachers, att_date=att_date)


# ----------------------- REST API (for mobile app / external use) -----------------------
# All /api/v1/* endpoints require header:  X-API-KEY: <your key>

@app.route("/api/v1/students", methods=["GET"])
@api_key_required
def api_students():
    class_id = request.args.get("class_id", type=int)
    q = Student.query
    if class_id:
        q = q.filter_by(class_id=class_id)
    data = [{
        "id": s.id, "name": s.name, "roll": s.roll,
        "class": s.school_class.name if s.school_class else None,
        "section": s.section.name if s.section else None,
        "father_name": s.father_name, "mother_name": s.mother_name,
        "phone": s.phone, "address": s.address,
        "photo": url_for("static", filename=f"uploads/{s.photo}", _external=True) if s.photo else None
    } for s in q.all()]
    return jsonify(data)


@app.route("/api/v1/students", methods=["POST"])
@api_key_required
def api_add_student():
    payload = request.get_json(force=True)
    s = Student(
        name=payload.get("name"),
        roll=payload.get("roll"),
        class_id=payload.get("class_id"),
        section_id=payload.get("section_id"),
        father_name=payload.get("father_name"),
        mother_name=payload.get("mother_name"),
        phone=payload.get("phone"),
        address=payload.get("address"),
        admission_date=payload.get("admission_date"),
    )
    db.session.add(s)
    db.session.commit()
    return jsonify({"message": "created", "id": s.id}), 201


@app.route("/api/v1/teachers", methods=["GET"])
@api_key_required
def api_teachers():
    data = [{
        "id": t.id, "name": t.name, "designation": t.designation,
        "phone": t.phone, "email": t.email, "address": t.address,
        "photo": url_for("static", filename=f"uploads/{t.photo}", _external=True) if t.photo else None
    } for t in Teacher.query.all()]
    return jsonify(data)


@app.route("/api/v1/attendance/students", methods=["GET"])
@api_key_required
def api_student_attendance():
    att_date = request.args.get("date", date.today().isoformat())
    records = StudentAttendance.query.filter_by(date=att_date).all()
    data = [{"student_id": r.student_id, "student_name": r.student.name, "date": r.date, "status": r.status} for r in records]
    return jsonify(data)


@app.route("/api/v1/attendance/students", methods=["POST"])
@api_key_required
def api_mark_student_attendance():
    payload = request.get_json(force=True)
    student_id = payload.get("student_id")
    att_date = payload.get("date", date.today().isoformat())
    status = payload.get("status", "Present")
    existing = StudentAttendance.query.filter_by(student_id=student_id, date=att_date).first()
    if existing:
        existing.status = status
    else:
        db.session.add(StudentAttendance(student_id=student_id, date=att_date, status=status))
    db.session.commit()
    return jsonify({"message": "saved"})


@app.route("/api/v1/attendance/teachers", methods=["GET"])
@api_key_required
def api_teacher_attendance():
    att_date = request.args.get("date", date.today().isoformat())
    records = TeacherAttendance.query.filter_by(date=att_date).all()
    data = [{"teacher_id": r.teacher_id, "teacher_name": r.teacher.name, "date": r.date, "status": r.status} for r in records]
    return jsonify(data)


@app.route("/api/v1/attendance/teachers", methods=["POST"])
@api_key_required
def api_mark_teacher_attendance():
    payload = request.get_json(force=True)
    teacher_id = payload.get("teacher_id")
    att_date = payload.get("date", date.today().isoformat())
    status = payload.get("status", "Present")
    existing = TeacherAttendance.query.filter_by(teacher_id=teacher_id, date=att_date).first()
    if existing:
        existing.status = status
    else:
        db.session.add(TeacherAttendance(teacher_id=teacher_id, date=att_date, status=status))
    db.session.commit()
    return jsonify({"message": "saved"})


@app.route("/api/v1/dashboard", methods=["GET"])
@api_key_required
def api_dashboard():
    inst = Institute.query.first()
    return jsonify({
        "institute_name": inst.name if inst else "",
        "institute_id": inst.institute_id if inst else "",
        "academic_year": inst.academic_year if inst else "",
        "total_students": Student.query.count(),
        "total_teachers": Teacher.query.count(),
        "total_classes": SchoolClass.query.count(),
    })


# ----------------------- DB INIT -----------------------

def init_db():
    with app.app_context():
        db.create_all()
        if not Institute.query.first():
            db.session.add(Institute(
                name="Mojidpur Central School",
                address="Chungripar, Mojidpur, Savar, Dhaka",
                phone="+8801799992387",
                email="mojidpurcentralschool@gmail.com",
                institute_id="92387",
                academic_year="2026",
            ))
        if not User.query.filter_by(username="admin").first():
            u = User(username="admin", role="admin")
            u.set_password("admin123")
            db.session.add(u)
        db.session.commit()


# Ensure the database and default admin user exist whether the app is run
# directly (python app.py) or imported by a production server (gunicorn app:app)
init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
