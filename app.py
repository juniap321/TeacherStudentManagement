# app.py
from flask import Flask, jsonify, request
from config import Config
from models import db, Student, Teacher, TeacherStudent, Log
from datetime import datetime
from sqlalchemy import text  # Import text to handle raw SQL queries

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# Create the database tables if they don't exist
with app.app_context():
    db.create_all()

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    role = data.get('role')  # 'student' or 'teacher'
    
    if not name or not email or role not in ['student', 'teacher']:
        return jsonify({"error": "Invalid data"}), 400
    
    try:
        if role == 'student':
            # Check if student exists
            student_exists = db.session.execute(text("SELECT * FROM student_management WHERE email = :email"), {'email': email}).fetchone()
            if student_exists:
                return jsonify({"error": "Student already registered"}), 400
            # Insert student into the database
            db.session.execute(text("INSERT INTO student_management (name, email) VALUES (:name, :email)"), {'name': name, 'email': email})
        
        elif role == 'teacher':
            # Check if teacher exists
            teacher_exists = db.session.execute(text("SELECT * FROM teacher_management WHERE email = :email"), {'email': email}).fetchone()
            if teacher_exists:
                return jsonify({"error": "Teacher already registered"}), 400
            # Insert teacher into the database
            db.session.execute(text("INSERT INTO teacher_management (name, email) VALUES (:name, :email)"), {'name': name, 'email': email})

        db.session.commit()
        return jsonify({"message": f"{role.capitalize()} registered successfully!"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    role = data.get('role')  # 'student' or 'teacher'

    if not email or role not in ['student', 'teacher']:
        return jsonify({"error": "Invalid data"}), 400

    try:
        user = None
        if role == 'student':
            user = db.session.execute(text("SELECT id, name FROM student_management WHERE email = :email"), {'email': email}).fetchone()
        
        elif role == 'teacher':
            user = db.session.execute(text("SELECT id, name FROM teacher_management WHERE email = :email"), {'email': email}).fetchone()

        if user is None:
            return jsonify({"error": "Invalid email or role"}), 404

        # Log the login attempt
        db.session.execute(
            text("INSERT INTO logs (user_id, user_name, sign_in_time) VALUES (:user_id, :user_name, :sign_in_time)"),
            {'user_id': user.id, 'user_name': user.name, 'sign_in_time': datetime.utcnow()}
        )
        db.session.commit()
        
        return jsonify({"message": f"{role.capitalize()} logged in successfully!"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500



# View all students
@app.route('/students', methods=['GET'])
def view_students():
    try:
        students = db.session.execute(text("SELECT id, name, email FROM student_management")).fetchall()
        # Convert the result to a list of dictionaries
        student_list = [{"id": student.id, "name": student.name, "email": student.email} for student in students]
        return jsonify(student_list), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Update student
@app.route('/update_student/<int:id>', methods=['PATCH'])
def update_student(id):
    data = request.json
    name = data.get('name')
    email = data.get('email')

    if not name or not email:
        return jsonify({"error": "Name and email are required to update"}), 400

    try:
        db.session.execute(
            text("UPDATE student_management SET name = :name, email = :email WHERE id = :id"),
            {'name': name, 'email': email, 'id': id}
        )
        db.session.commit()
        
        return jsonify({"message": "Student updated successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# Delete student
@app.route('/delete_student/<int:id>', methods=['DELETE'])
def delete_student(id):
    try:
        # Execute the delete query
        result = db.session.execute(text("DELETE FROM student_management WHERE id = :id"), {'id': id})
        db.session.commit()

        if result.rowcount == 0:
            return jsonify({"error": "Student not found"}), 404

        return jsonify({"message": "Student deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500




#teacher list

@app.route('/get_teachers/<int:student_id>', methods=['GET'])
def get_teachers(student_id):
    try:
        # Query to get all teachers for the specified student
        teachers = db.session.execute(
            text("""
                SELECT t.id, t.name, t.email 
                FROM teacher_management AS t
                JOIN teacher_student AS ts ON t.id = ts.teacher_id
                WHERE ts.student_id = :student_id
            """), {'student_id': student_id}
        ).fetchall()

        # Convert result to list of dictionaries
        teacher_list = [{"id": teacher.id, "name": teacher.name, "email": teacher.email} for teacher in teachers]

        if not teacher_list:
            return jsonify({"message": "No teachers found for this student"}), 404

        return jsonify(teacher_list), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
