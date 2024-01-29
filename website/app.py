from flask import Flask, render_template

app = Flask(__name__, template_folder='templates', static_url_path='/static')

@app.route('/')
@app.route('/home')

def index():
    return render_template('index.html')


@app.route('/teacher')
def teacher():
    return render_template('teacher.html')
