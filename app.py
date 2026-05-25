from flask import Flask, render_template, request,redirect,session
import sqlite3

app = Flask(__name__)
app.secret_key = 'secret123'
# Create database table
def init_db():
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            roll TEXT,
            department TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            date TEXT,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == 'admin123':

            session['user'] = username

            return redirect('/students')

        else:
            return "Invalid Username or Password"

    return render_template('login.html')
# Home page
@app.route('/')
def home():
    return render_template('index.html')

# Add student
@app.route('/add', methods=['POST'])
def add_student():
    name = request.form['name']
    roll = request.form['roll']
    department = request.form['department']

    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO students (name, roll, department) VALUES (?, ?, ?)",
        (name, roll, department)
    )

    conn.commit()
    conn.close()

    return redirect('/students')
@app.route('/students')
def view_students():
    if 'user' not in session:
        return redirect('/login')

    search = request.args.get('search')

    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()

    if search:

        cursor.execute(
            "SELECT * FROM students WHERE name LIKE ?",
            ('%' + search + '%',)
        )

    else:

        cursor.execute("SELECT * FROM students")

    students = cursor.fetchall()

    conn.close()

    return render_template('students.html', students=students)
@app.route('/delete/<int:id>')
def delete_student(id):

    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()

    cursor.execute("DELETE FROM students WHERE id = ?", (id,))

    conn.commit()
    conn.close()

    return redirect('/students')
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):

    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()

    # When form is submitted
    if request.method == 'POST':

        name = request.form['name']
        roll = request.form['roll']
        department = request.form['department']

        cursor.execute(
            "UPDATE students SET name=?, roll=?, department=? WHERE id=?",
            (name, roll, department, id)
        )

        conn.commit()
        conn.close()

        return redirect('/students')

    # Load existing student data
    cursor.execute("SELECT * FROM students WHERE id=?", (id,))
    student = cursor.fetchone()

    conn.close()

    return render_template('edit.html', student=student)
@app.route('/attendance', methods=['GET', 'POST'])
def attendance():

    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()

    # When attendance form submitted
    if request.method == 'POST':

        date = request.form['date']

        cursor.execute("SELECT * FROM students")
        students = cursor.fetchall()

        for student in students:

            student_id = student[0]

            status = request.form.get(f'attendance_{student_id}')

            cursor.execute(
                "INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)",
                (student_id, date, status)
            )

        conn.commit()
        conn.close()

        return "Attendance Saved Successfully"
@app.route('/view_attendance')
def view_attendance():

    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT students.name,
               attendance.date,
               attendance.status

        FROM attendance

        JOIN students
        ON attendance.student_id = students.id
    ''')

    records = cursor.fetchall()

    conn.close()

    return render_template(
        'view_attendance.html',
        records=records
    )
@app.route('/attendance_report')
def attendance_report():

    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT students.name,

        COUNT(CASE WHEN attendance.status = 'Present'
              THEN 1 END) * 100.0 / COUNT(attendance.id)

        AS percentage

        FROM attendance

        JOIN students
        ON attendance.student_id = students.id

        GROUP BY students.id
    ''')

    reports = cursor.fetchall()

    conn.close()

    return render_template(
        'attendance_report.html',
        reports=reports
    )
    # Load students
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    conn.close()

    return render_template('attendance.html', students=students)
@app.route('/logout')
def logout():

    session.pop('user', None)

    return redirect('/login')
if __name__ == '__main__':
    init_db()
    app.run(debug=True)