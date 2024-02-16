from flask import Flask, render_template, request, flash, redirect, send_from_directory, Response, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import MySQLdb.cursors, re, hashlib
import pandas as pd
import os
from io import StringIO



app = Flask(__name__, template_folder='templates', static_url_path='/static')
app.secret_key = 'ching chong ding dong'

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'kindergarten_system'

mysql = MySQL(app)

def fetch_data(table_name):
    cur = mysql.connection.cursor()
    cur.execute(f"SELECT * FROM {table_name}")
    data = cur.fetchall()
    cur.close()
    return data
    
@app.route('/')
def start():
    return render_template('login.html')


@app.route('/admin')
def admin():
    employees_data = fetch_data('employees')
    studentlistattendance_data = fetch_data('studentlistattendance')

    # Get the list of generated CSV filenames (adjust the path accordingly)
    csv_folder_path = 'uploads'
    filenames = [f for f in os.listdir(csv_folder_path) if f.endswith('.csv')]

    return render_template('index.html', employees=employees_data, studentlistattendance=studentlistattendance_data, filenames=filenames, accountname= session['accountname'])



@app.route('/uploadcsv', methods=['POST'])
def uploadcsv():
    try:
        if 'csvFile' not in request.files:
            flash('No file part', 'csv_error')
            return redirect(url_for('admin'))

        csv_file = request.files['csvFile']

        if csv_file.filename == '':
            flash('No selected file', 'csv_error')
            return redirect(url_for('admin'))

        if csv_file and csv_file.filename.endswith('.csv'):
            # Read CSV into a DataFrame
            df = pd.read_csv(csv_file)

            # Ensure that the required columns are present in the DataFrame
            required_columns = {'student id', 'name', 'class', 'status'}
            if not required_columns.issubset(df.columns.str.strip().str.lower()):
                flash('Invalid CSV file format. Headers should be "Student ID, Name, Class, Status"', 'csv_error')
                return redirect(url_for('admin'))

            # Process the DataFrame
            cur = mysql.connection.cursor()
            for _, row in df.iterrows():
                student_id = row['Student ID']
                cur.execute("SELECT student_id FROM studentlistattendance WHERE student_id = %s", (student_id,))
                existing_row = cur.fetchone()                
                
                if existing_row is None:
                    cur.execute("""
                        INSERT INTO studentlistattendance (student_id, name, class, status) 
                        VALUES (%s, %s, %s, %s);
                    """, (row['Student ID'], row['Name'], row['Class'], row['Status']))
                else:
                    flash(f'Student ID {student_id} already exists in the database', 'csv_error')

            mysql.connection.commit()
            flash('CSV File Uploaded Successfully', 'csv_success')

            # Generate CSV files and serve them dynamically
            class_values = df['Class'].unique()
            for class_value in class_values:
                class_df = df[df['Class'] == class_value]
                csv_content = class_df[['Student ID', 'Name']].to_csv(index=False, lineterminator='\n')
                csv_filename = f"Class {class_value} Student List.csv"  # Adjust the filename pattern if needed

                # Save the CSV content to the 'uploads' folder
                csv_filepath = os.path.join('uploads', csv_filename)
                with open(csv_filepath, 'w') as csv_file:
                    csv_file.write(csv_content)

    except Exception as e:
        flash(f'Error processing CSV file: {str(e)}', 'csv_error')

    return redirect(url_for('admin'))

@app.route('/download_csv/<filename>')
def download_csv(filename):
    # Assuming the generated CSV files are stored in the 'uploads' folder
    csv_folder_path = 'uploads'
    return send_from_directory(csv_folder_path, filename, as_attachment=True)


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
        return redirect(url_for('admin'))

@app.route('/delete/<string:id_data>', methods=['GET'])
def delete(id_data):
    flash('Data Deleted Successfully', 'employee_success')
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM employees WHERE id=%s", (id_data,))
    mysql.connection.commit()
    return redirect(url_for('admin'))


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
        return redirect(url_for('admin'))
        

@app.route('/teacher')
def teacher():
    return render_template('teacher.html', accountname= session['accountname'])



@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and "accountname" in request.form and "password" in request.form:
        accountname = request.form['accountname']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM account WHERE accountname = %s AND password = %s', (accountname, password))

        account = cursor.fetchone()
        if account:
            session["loggedin"] = True
            session['id'] = account['id']
            session['accountname'] = account['accountname']

            if account['type'] == 'Admin':
                return redirect(url_for('admin'))
            elif account['type'] == 'Teacher':
                return redirect(url_for('teacher'))

        else:
            msg = 'Incorrect account name or password!'

    return render_template('login.html', msg=msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('accountname', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ""

    if request.method == 'POST' and 'accountname' in request.form and 'password' in request.form and 'role_type' in request.form:
        accountname = request.form['accountname']
        password = request.form['password']
        role_type = request.form['role_type']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM account WHERE accountname = %s', (accountname,))
        account = cursor.fetchone()
    
        if account:
            msg = 'Account already exists!'
        
        # Check if password length is at least 8 characters
        elif len(password) < 8:
            msg = 'Password must be at least 8 characters long!'

        # check if any radio button is selected
        elif role_type == '':
            msg = 'Please select a role type!'

        elif not accountname or not password or not role_type:
            msg = 'Please fill out the details!'

        else:
            cursor.execute('INSERT INTO account (accountname, password, type) VALUES (%s, %s, %s)', (accountname, password, role_type))
            mysql.connection.commit()
            flash('Your account is successfully registered!', 'register_success')
            return redirect(url_for('login'))

    return render_template('register.html', msg=msg)

def insert_assessment(Class, Subject, Assesssment, Name, Marks):
    # Insert assessment data into the database
    query = "INSERT INTO assessment (Class, Subject, Assesssment, Name, Marks) VALUES (%s, %s, %s, %s, %s)"
    values = (Class, Subject, Assesssment, Name, Marks)
    cur = mysql.connection.cursor()
    cur.execute(query, values)
    mysql.connection.commit()

@app.route('/submit_assessment', methods=['POST'])
def submit_assessment():
    if 'confirm_button' in request.form:
        # Process form data and insert into the database
        Class = request.form.get('Class')
        Subject = request.form.get('Subject')
        Assesssment = request.form.get('Assesssment')
        Name = request.form.get('Name')
        Marks = request.form.get('Marks')

        insert_assessment(Class, Subject, Assesssment, Name, Marks)

        flash('Assessment submitted successfully!', 'assessment_success')

    else:
        flash('Please confirm the assessment submission!', 'assessment_error')

    return redirect(url_for('teacher'))

if __name__ == '__main__':
    app.run(debug=True)

