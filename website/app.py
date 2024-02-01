from flask import Flask, render_template, request, url_for, flash, redirect, send_from_directory
from flask_mysqldb import MySQL
import pandas as pd


app = Flask(__name__, template_folder='templates', static_url_path='/static')
app.secret_key = 'ching chong ding dong'

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Jacklim2626'
app.config['MYSQL_DB'] = 'kindergarten_system'

mysql = MySQL(app)

def fetch_data(table_name):
    cur = mysql.connection.cursor()
    cur.execute(f"SELECT * FROM {table_name}")
    data = cur.fetchall()
    cur.close()
    return data
    
@app.route('/')
def index():
    employees_data = fetch_data('employees')
    studentlistattendance_data = fetch_data('studentlistattendance')

    # active_tab = int(request.args.get('active_tab', 1))

    return render_template('index.html', employees=employees_data, studentlistattendance=studentlistattendance_data)

@app.route('/uploadcsv', methods=['POST'])
def uploadcsv():
    try:
        if 'csvFile' not in request.files:
            flash('No file part', 'csv_error')
            return redirect(url_for('index'))

        csv_file = request.files['csvFile']

        if csv_file.filename == '':
            flash('No selected file', 'csv_error')
            return redirect(url_for('index'))

        if csv_file and csv_file.filename.endswith('.csv'):
            # Read CSV into a DataFrame
            df = pd.read_csv(csv_file)

            # Ensure that the required columns are present in the DataFrame
            required_columns = {'student id', 'name', 'class', 'status'}
            if not required_columns.issubset(df.columns.str.strip().str.lower()):
                flash('Invalid CSV file format. Headers should be "Student ID, Name, Class, Status"', 'csv_error')
                return redirect(url_for('index'))

            # Process the DataFrame
            cur = mysql.connection.cursor()
            for _, row in df.iterrows():
                cur.execute("""
                    INSERT INTO studentlistattendance (student_id, name, class, status) 
                    VALUES (%s, %s, %s, %s);
                """, (row['Student ID'], row['Name'], row['Class'], row['Status']))

            mysql.connection.commit()
            flash('CSV File Uploaded Successfully', 'csv_success')
        else:
            flash('Invalid File. Please upload a CSV file.', 'csv_error')
    except Exception as e:
        flash(f'Error processing CSV file: {str(e)}', 'csv_error')

    return redirect(url_for('index'))


@app.route('/download_template')
def download_template():
    template_filename = 'Student_List_Template.csv'
    return send_from_directory('static', template_filename, as_attachment=True)

@app.route('/insert', methods=['POST'])
def insert():
    if request.method == 'POST':
        flash('Data Inserted Successfully', 'employee_success')
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
    flash('Data Deleted Successfully', 'employee_success')
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
        flash("Data Updated Successfully", "employee_success")
        return redirect(url_for('index'))

@app.route('/teacher')
def teacher():
    return render_template('teacher.html')

if __name__ == '__main__':
    app.run(debug=True)
