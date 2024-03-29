from flask import Flask, render_template, request, flash, redirect, send_from_directory, Response, url_for, session
from flask_mysqldb import MySQL
from flask_mail import Mail, Message
from uuid import uuid4
import MySQLdb.cursors
import MySQLdb.cursors, re, hashlib
import pandas as pd
import os
import json
import ast
from io import StringIO


app = Flask(__name__, template_folder='templates', static_url_path='/static')

app.secret_key = 'ching chong ding dong'

# Mail configurations
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'jacklim2626@gmail.com'
app.config['MAIL_PASSWORD'] = 'snjaavjmnrnwdnny'
app.config['MAIL_DEFAULT_SENDER'] = 'jacklim2626@gmail.com'


# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'kindergarten_system'

mail = Mail(app)
mysql = MySQL(app)

def fetch_distinct_class():
    cur = mysql.connection.cursor()
    cur.execute("SELECT DISTINCT class FROM studentprofile")
    classes = cur.fetchall()
    cur.close()
    return classes


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
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    else:
        selected_class = request.args.get('class')

        classes = fetch_distinct_class()
        employees_data = fetch_data('employees')
        studentlistattendance_data = fetch_data('studentlistattendance')
        
        studentprofile_data = []
        if selected_class:
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM studentprofile WHERE class = %s", (selected_class,))
            studentprofile_data = cur.fetchall()
            cur.close()

        # Get the list of generated CSV filenames (adjust the path accordingly)
        csv_folder_path = 'uploads'
        filenames = [f for f in os.listdir(csv_folder_path) if f.endswith('.csv')]

        return render_template('index.html', classes=classes, employees=employees_data, studentlistattendance=studentlistattendance_data, studentprofile=studentprofile_data, filenames=filenames, accountname=session['accountname'], selected_class=selected_class)


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
        
def fetch_distinct_class01():
    cur = mysql.connection.cursor()
    cur.execute("SELECT DISTINCT class FROM termreport")
    classes01 = cur.fetchall()
    cur.close()
    return classes01

def fetch_distinct_class02():
    cur = mysql.connection.cursor()
    cur.execute("SELECT DISTINCT class FROM studentlistattendance")
    classes02 = cur.fetchall()
    cur.close()
    return classes02

@app.route('/teacher')
def teacher():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    else:
        if request.method == 'GET':
            selected_class01 = request.args.get('class_term')
            selected_class02 = request.args.get('class_attend')
            teacher_profile = fetch_data('teacher_profile')
        
            classes01 = fetch_distinct_class01()
            classes02 = fetch_distinct_class02()


            termreport_data = []
            if selected_class01:
                cur = mysql.connection.cursor()
                cur.execute("SELECT * FROM termreport WHERE class = %s", (selected_class01,))
                termreport_data = cur.fetchall()
                cur.close()
                
            attendance_data = []
            if selected_class02:
                cur = mysql.connection.cursor()
                cur.execute("SELECT * FROM studentlistattendance WHERE class = %s", (selected_class02,))
                attendance_data = cur.fetchall()
                cur.close()
            

            return render_template('teacher.html', termreport=termreport_data, attendance=attendance_data, classes01=classes01, classes02=classes02,accountname= session['accountname'], teacher_profile=teacher_profile)        


@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and "accountname" in request.form and "password" in request.form:
        accountname = request.form['accountname']
        password = request.form['password']

        hash_pass = hashlib.md5(password.encode('utf-8')).hexdigest()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM account WHERE accountname = %s AND password = %s', (accountname, hash_pass))

        account = cursor.fetchone()
        if account:
            session["loggedin"] = True
            session['id'] = account['id']
            session['accountname'] = account['accountname']
            session['type'] = account['type']

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

    if request.method == 'POST' and 'accountname' in request.form and 'email' in request.form and 'password' in request.form and 'role_type' in request.form:
        accountname = request.form['accountname']
        email = request.form['email']
        password = request.form['password']
        role_type = request.form['role_type']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM account WHERE accountname = %s', (accountname,))
        account = cursor.fetchone()
        cursor.execute('SELECT * FROM account WHERE email = %s', (email,))
        email_db = cursor.fetchone()
    
        if account:
            msg = 'Account already exists!'

        elif email_db:
            msg = 'Email already exists!'
        
        # Check if password length is at least 8 characters
        elif len(password) < 8:
            msg = 'Password must be at least 8 characters long!'

        # check if any radio button is selected
        elif role_type == '':
            msg = 'Please select a role type!'

        else:
            hash_pass = hashlib.md5(password.encode('utf-8')).hexdigest()

            cursor.execute('INSERT INTO account (accountname, email, password, type) VALUES (%s, %s, %s, %s)', (accountname, email, hash_pass, role_type))
            mysql.connection.commit()
            flash('Your account is successfully registered!', 'register_success')
            return redirect(url_for('login'))

    return render_template('register.html', msg=msg)


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == "POST":
        email = request.form['email']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM account WHERE email = %s', (email,))
        user = cursor.fetchone()

        if user:
            reset_token = uuid4()

            cursor.execute('UPDATE account SET reset_token = %s WHERE email = %s', (reset_token, email))
            mysql.connection.commit()

            reset_link = url_for('reset_password', token=reset_token, _external=True)
            msg = Message('Password Reset Request', recipients=[email])
            msg.body = f"To reset your password, visit the following link: {reset_link}"
            mail.send(msg)
            flash('An email with instructions to reset your password has been sent to your email address.', 'email_success')
        else:
            flash('Email address not found. Please make sure you entered the correct email.', 'email_error')

    return render_template('forgot_password.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if request.method == 'POST':
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if new_password != confirm_password:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('reset_password', token=token))

        # Hash the new password
        hashed_password = hashlib.md5(new_password.encode('utf-8')).hexdigest()

        # Update the user's password in the database
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE account SET password = %s, reset_token = NULL WHERE reset_token = %s', (hashed_password, token))
        mysql.connection.commit()

        flash('Password reset successful!', 'reset_success')
        return redirect(url_for('login'))

        # Verify the reset token
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM account WHERE reset_token = %s', (token,))
        user = cursor.fetchone()

        if not user:
            flash('Invalid or expired reset token!', 'reset_error')
            return redirect(url_for('login'))

    return render_template('reset_password.html', token=token)

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


@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    try:
        if 'loggedin' not in session:
            return redirect(url_for('login'))

        if request.method == 'POST':
            old_password = request.form.get('old_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')

            # Validate old password
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM account WHERE id = %s', (session['id'],))
            account = cursor.fetchone()

            hash_old_pass = hashlib.md5(old_password.encode('utf-8')).hexdigest()

            if account and hash_old_pass == account['password']:
                # Validate new password
                if new_password == confirm_password:
                    if len(new_password) >= 8:
                        # Update password in the database
                        hash_new_pass = hashlib.md5(new_password.encode('utf-8')).hexdigest()

                        cursor.execute('UPDATE account SET password = %s WHERE id = %s', (hash_new_pass, session['id']))
                        mysql.connection.commit()
                        flash('Password changed successfully!', 'password_success')

                        if account['type'] == 'Admin':
                            return redirect(url_for('admin'))
                        elif account['type'] == 'Teacher':
                            return redirect(url_for('teacher'))
                        
                    else:
                        flash('Password must be at least 8 characters long!', 'password_error')
                else:
                    flash('New password and confirmation password do not match!', 'password_error')
            else:
                flash('Incorrect old password!', 'password_error')
    except Exception as e:
        flash(f'Error changing password: {str(e)}', 'password_error')
    
    if account['type'] == 'Teacher':
        return redirect(url_for('teacher'))
    elif account['type'] == 'Admin':
        return redirect(url_for('admin'))

@app.route('/add_studentprofile', methods=['POST'])
def add_studentprofile():
    try:
        if request.method == 'POST':
            student_name = request.form.get('student_name')
            student_id = request.form.get('student_id')
            class_value = request.form.get('class')
            parent_name = request.form.get('parent_name')
            parent_contact = request.form.get('parent_contact')

            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO studentprofile (student_id, name, class, parentname, parentcontact)
                VALUES (%s, %s, %s, %s, %s)
                """, (student_id, student_name, class_value, parent_name, parent_contact))
            mysql.connection.commit()
            flash('Student profile added successfully!', 'studentprofile_success')
            return redirect(url_for('admin'))            
            
    except Exception as e:
        flash(f'Error adding student profile: {str(e)}', 'studentprofile_error')

    return redirect(url_for('admin'))


@app.route('/update_studentprofile', methods=['POST'])
def update_studentprofile():
    try:
        if request.method == 'POST':
            student_id = request.form.get('student_id')
            student_name = request.form.get('student_name')
            class_value = request.form.get('class')
            parent_name = request.form.get('parent_name')
            parent_contact = request.form.get('parent_contact')

            cur = mysql.connection.cursor()
            cur.execute("""
                UPDATE studentprofile SET name=%s, class=%s, parentname=%s, parentcontact=%s 
                WHERE student_id=%s
                """, (student_name, class_value, parent_name, parent_contact, student_id))
            mysql.connection.commit()
            flash('Student profile updated successfully!', 'studentprofile_success')

    except Exception as e:
        flash(f'Error updating student profile: {str(e)}', 'studentprofile_error')

    return redirect(url_for('admin'))


@app.route('/delete_studentprofile/<int:student_id>', methods=['GET'])
def delete_studentprofile(student_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM studentprofile WHERE student_id=%s", (student_id,))
        mysql.connection.commit()
        flash('Student profile deleted successfully!', 'studentprofile_success')
    except Exception as e:
        flash(f'Error deleting student profile: {str(e)}', 'studentprofile_error')
    
    return redirect(url_for('admin'))


@app.route('/add_termreport', methods=['POST'])
def add_termreport():
    try:
        if request.method == 'POST':
            student_id = request.form.get('student_id')
            student_name = request.form.get('student_name')
            class_value = request.form.get('class_name')
            english = request.form.get('english')
            malay = request.form.get('malay')
            chinese = request.form.get('chinese')
            math = request.form.get('math')

            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO termreport (studentid, class, name, english, malay, chinese, math)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (student_id, class_value, student_name, english, malay, chinese, math))
            mysql.connection.commit()
            flash('Term report added successfully!', 'termreport_success')
    
    except Exception as e:
        flash(f'Error adding term report: {str(e)}', 'termreport_error')

    return redirect(url_for('teacher'))


@app.route('/update_termreport', methods=['POST'])
def update_termreport():
    try:
        if request.method == 'POST':
            student_id = request.form.get('student_id')
            english = request.form.get('english')
            malay = request.form.get('malay')
            chinese = request.form.get('chinese')
            math = request.form.get('math')

            cur = mysql.connection.cursor()
            cur.execute("""
                UPDATE termreport SET english=%s, malay=%s, chinese=%s, math=%s 
                WHERE studentid=%s
                """, (english, malay, chinese, math, student_id))
            mysql.connection.commit()
            flash('Term report updated successfully!', 'termreport_success')

    except Exception as e:
        flash(f'Error updating term report: {str(e)}', 'termreport_error')
    
    return redirect(url_for('teacher'))
    
@app.route('/delete_termreport/<int:student_id>', methods=['GET'])
def delete_termreport(student_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM termreport WHERE studentid=%s", (student_id,))
        mysql.connection.commit()
        flash('Term report deleted successfully!', 'termreport_success')
    except Exception as e:
        flash(f'Error deleting term report: {str(e)}', 'termreport_error')
    
    return redirect(url_for('teacher'))

@app.route('/confirm_attendance', methods=['POST'])
def confirm_attendance():
    try:
        if request.method == 'POST':
            studentid = request.form.get('student_id')
            selected_class = request.form.get('class')
            attendance_checkboxes = request.form.getlist('attendanceCheckbox')
            action = request.form.get('action')  # Getting the value of the clicked button

            if attendance_checkboxes and selected_class and studentid and action:
                cur = mysql.connection.cursor()
                if action == 'absent':
                    cur.execute("UPDATE studentlistattendance SET status = 'Absent' WHERE class = %s AND student_id = %s", (selected_class, studentid))
                    flash('Marked as absent successfully!', 'attendance_success')
                elif action == 'present':
                    cur.execute("UPDATE studentlistattendance SET status = 'Present' WHERE class = %s AND student_id = %s", (selected_class, studentid))
                    flash('Marked as present successfully!', 'attendance_success')
                mysql.connection.commit()
            else:
                flash('Invalid form data!', 'attendance_error')

    except Exception as e:
        flash(f'Error confirming attendance: {str(e)}', 'attendance_error')

    return redirect(url_for('teacher'))

@app.route('/update_profile', methods=['POST'])
def update_profile():
    teacher_profile = fetch_data('teacher_profile')
    account_id = session['id']
    
    try:

        if request.method == 'POST':
            teacher_id = request.form.get('teacher_id')
            teacher_name = request.form.get('teacher_name')
            nric = request.form.get('NRIC')
            contact = request.form.get('contact')
            department = request.form.get('department')
            qualification = request.form.get('qualification')
            experience = request.form.get('experience')
            bio = request.form.get('bio')

            for teacher in teacher_profile:
                if teacher[0] == account_id:
                    cur = mysql.connection.cursor()
                    cur.execute("""
                            UPDATE teacher_profile SET name=%s, nric=%s, contact=%s, department=%s, qualification=%s, experience=%s, bio=%s
                            WHERE id=%s
                            """, (teacher_name, nric, contact, department, qualification, experience, bio, teacher_id))
                    mysql.connection.commit()
                    flash('Teacher profile updated successfully!', 'profile_success')
                    return redirect(url_for('teacher'))
            flash('You are not authorized to update this profile.', 'profile_error')
            return redirect(url_for('teacher'))

    except Exception as e:
        flash(f'Error updating profile: {str(e)}', 'profile_error')
    
    return redirect(url_for('teacher'))
        

@app.route('/add_teacherprofile', methods=['POST'])
def add_teacherprofile():
    try:
        if request.method == 'POST':
            teacher_id = request.form.get('teacher_id')
            account_type = request.form.get('account_type')
            teacher_name = request.form.get('teacher_name')
            nric = request.form.get('NRIC')
            contact = request.form.get('contact')
            department = request.form.get('department')
            qualification = request.form.get('qualification')
            experience = request.form.get('experience')
            bio = request.form.get('bio')

            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO teacher_profile (id, type, name, nric, contact, department, qualification, experience, bio)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (teacher_id, account_type, teacher_name, nric, contact, department, qualification, experience, bio))
            mysql.connection.commit()
            flash('Teacher profile added successfully!', 'teacherprofile_success')
            return redirect(url_for('teacher'))

    except Exception as e:
        flash(f'Error adding teacher profile: {str(e)}', 'teacherprofile_error')

    return redirect(url_for('teacher'))

if __name__ == '__main__':
    app.run(debug=True)