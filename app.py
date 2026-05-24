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
@app.route('/logout')
def logout():

    session.pop('user', None)

    return redirect('/login')
if __name__ == '__main__':
    init_db()
    app.run(debug=True)