from flask import Flask, render_template, request, redirect, url_for, flash
import csv
import os

# Initialize Flask with explicit static folder settings so that image paths in home.html and contact.html work correctly.
app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = 'replace_with_your_secret_key'

DATA_FILE = 'data.csv'

# Ensure the CSV file exists with headers
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['first_name', 'last_name', 'username', 'email', 'password'])

@app.route('/')
def index():
    # Render the landing page (home.html)
    return render_template('home.html')

@app.route('/login.html', methods=['GET'])
def login_page():
    # Render the login page when accessed via GET
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    authenticated = False
    username = ''

    # Read CSV file to check credentials
    with open(DATA_FILE, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['email'] == email and row['password'] == password:
                authenticated = True
                username = row['username']
                break

    if authenticated:
        # On successful login, redirect to index.html (the main page) and share the username via a query parameter.
        return redirect(url_for('main_page', username=username))
    else:
        flash('Invalid email or password', 'error')
        return redirect(url_for('login_page', status='error'))

@app.route('/signup', methods=['POST'])
def signup():
    first_name = request.form.get('first_n')
    last_name = request.form.get('last_n')
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')

    # Check if a user with this email already exists
    user_exists = False
    with open(DATA_FILE, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['email'] == email:
                user_exists = True
                break

    if user_exists:
        flash('User already exists with that email.', 'error')
        return redirect(url_for('login_page', status='error'))

    # Append the new user's data to data.csv
    with open(DATA_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([first_name, last_name, username, email, password])
    
    flash('Signup successful. Please log in.', 'success')
    return redirect(url_for('login_page'))

@app.route('/index.html')
def main_page():
    # Retrieve the username from query parameters (default to 'Guest' if not provided)
    username = request.args.get('username', 'Guest')
    # Render the main page (index.html) with the provided username for sharing between pages.
    return render_template('index.html', username=username)

@app.route('/contact.html')
def contact():
    # Render the contact page (contact.html)
    desktop_image = url_for('static', filename='desktop.png')
    return render_template('contact.html', desktop_image=desktop_image)

if __name__ == '__main__':
    app.run(debug=True)
