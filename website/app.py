from flask import Flask, render_template, request, url_for, flash, redirect
from flask_mysqldb import MySQL

app = Flask(__name__, template_folder='templates', static_url_path='/static')
app.secret_key = 'ching chong ding dong'

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Jacklim2626'
app.config['MYSQL_DB'] = 'kindergarten_system'

mysql = MySQL(app)

@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM employees")
    data = cur.fetchall()
    cur.close()

    return render_template('index.html', employees=data)

@app.route('/insert', methods=['POST'])
def insert():
    if request.method == 'POST':
        flash('Data Inserted Successfully')
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        gender = request.form['gender']
        classroom = request.form['class']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO employees (name, email, subject, gender, class) VALUES (%s, %s, %s, %s, %s)", (name, email, subject, gender, classroom))
        mysql.connection.commit()
        return redirect(url_for('index'))

@app.route('/delete/<string:id_data>', methods=['GET'])
def delete(id_data):
    flash('Data Deleted Successfully')
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM employees WHERE id=%s", (id_data,))
    mysql.connection.commit()
    return redirect(url_for('index'))


@app.route('/update', methods=['POST', 'GET'])
def update():
    if request.method == 'POST':
        id_data = request.form['id']
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        gender = request.form['gender']
        classroom = request.form['class']

        cur = mysql.connection.cursor()

        cur.execute("""
                UPDATE employees SET name=%s, email=%s, subject=%s, gender=%s, class=%s 
                WHERE id=%s
                """, (name, email, subject, gender, classroom, id_data))
        flash("Data Updated Successfully")
        return redirect(url_for('index'))

@app.route('/teacher')
def teacher():
    return render_template('teacher.html')

if __name__ == '__main__':
    app.run(debug=True)
