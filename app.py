import os
import hashlib
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

# Use Supabase PostgreSQL connection string for dataset
SUPABASE_DB_URL = "postgresql://postgres:[YOUR-PASSWORD]@db.mujedabghagsnioesygg.supabase.co:5432/postgres"

# Set base directory and template directory for cloud deployability
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')  # corrected directory name for templates
LOGIN_HTML_PATH = os.path.join(TEMPLATE_DIR, 'login.html')

app = Flask(__name__, template_folder=TEMPLATE_DIR)
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key_here')
app.config['SQLALCHEMY_DATABASE_URI'] = SUPABASE_DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define the User model corresponding to the users table in the database
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_n = db.Column(db.String(100), nullable=False)
    last_n = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)

    def __init__(self, first_n, last_n, username, email, password):
        self.first_n = first_n
        self.last_n = last_n
        self.username = username
        self.email = email
        self.password = password

def hash_data(data):
    # Hashes the given string using SHA256 and returns the hex digest.
    return hashlib.sha256(data.encode()).hexdigest()

def check_files_accessible():
    # Check if necessary template files are accessible (ignoring the database as it is handled via SQLAlchemy)
    if not os.path.exists(LOGIN_HTML_PATH):
        flash("The following file is not accessible: " + LOGIN_HTML_PATH)
        return False
    flash("All necessary files are accessible. (Verified: " + LOGIN_HTML_PATH + ")")
    return True

# Removed the home() route because the project no longer uses a home.html file.
# Instead, the root URL now redirects to the login route.
@app.route('/')
def root():
    return redirect(url_for('login'))

@app.route('/update', methods=['POST'])
def update():
    first_n = request.form.get('first_n', '')
    last_n = request.form.get('last_n', '')
    username = request.form.get('username', '')
    email = request.form.get('email', '')
    password = request.form.get('password', '')
    
    if not all([first_n, last_n, username, email, password]):
        flash('All fields are required.')
        return redirect(url_for('login'))
    
    # Hash the password and email for storage
    hashed_password = hash_data(password)
    hashed_email = hash_data(email)
    user = User.query.filter_by(username=username).first()
    
    if user:
        user.first_n = first_n
        user.last_n = last_n
        user.email = hashed_email
        user.password = hashed_password
        flash('User information updated successfully.')
    else:
        user = User(first_n, last_n, username, hashed_email, hashed_password)
        db.session.add(user)
        flash('New user added successfully.')
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error: {str(e)}")
        return "Error: Unable to update user information due to database issues.", 500
    
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if not check_files_accessible():
        return "Error: Some files are not accessible. Please check the server logs for more details.", 500
    
    if request.method == 'POST':
        email = request.form.get('email', '')
        password = request.form.get('password', '')
        
        if not all([email, password]):
            flash('Email and password are required.')
            return redirect(url_for('login', status='error'))
        
        hashed_email = hash_data(email)
        hashed_password = hash_data(password)
        user = User.query.filter_by(email=hashed_email, password=hashed_password).first()
        
        if user:
            flash('Login successful.')
            # After successful login, render the index page.
            return render_template('index.html')
        else:
            flash('Invalid email or password.')
            return redirect(url_for('login', status='error'))
    
    return render_template('login.html')

@app.route('/signup', methods=['POST'])
def signup():
    first_n = request.form.get('first_n', '')
    last_n = request.form.get('last_n', '')
    username = request.form.get('username', '')
    email = request.form.get('email', '')
    password = request.form.get('password', '')
    
    if not all([first_n, last_n, username, email, password]):
        flash('All fields are required.')
        return redirect(url_for('login'))
    
    # Hash password and email for storage
    hashed_password = hash_data(password)
    hashed_email = hash_data(email)
    
    if User.query.filter_by(username=username).first():
        flash('Username already exists.')
        return redirect(url_for('login'))
    
    new_user = User(first_n, last_n, username, hashed_email, hashed_password)
    db.session.add(new_user)
    
    try:
        db.session.commit()
        return redirect(url_for('login', status='signup_success'))
    except Exception as e:
        db.session.rollback()
        print(f"Error: {str(e)}")
        return "Error: Unable to save user information due to database issues.", 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
    port = int(os.environ.get('PORT', 5000))
    # Disable debug mode for cloud deployments unless explicitly set
    debug_mode = os.environ.get('DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
