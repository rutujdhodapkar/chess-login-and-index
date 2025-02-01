import os
import hashlib
import pandas as pd
import streamlit as st

# Set base directory and file paths
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
CSV_FILE_PATH = os.path.join(BASE_DIR, 'data.csv')

def hash_data(data):
    # Hashes the given string using SHA256 and returns the hex digest.
    return hashlib.sha256(data.encode()).hexdigest()

def initialize_csv():
    # Ensure the CSV file exists with the proper columns
    if not os.path.exists(CSV_FILE_PATH):
        pd.DataFrame(columns=['first_n', 'last_n', 'username', 'email', 'password']).to_csv(CSV_FILE_PATH, index=False)
    else:
        try:
            userinfo = pd.read_csv(CSV_FILE_PATH)
            if set(userinfo.columns) != {'first_n', 'last_n', 'username', 'email', 'password'}:
                userinfo.to_csv(CSV_FILE_PATH, index=False, header=['first_n', 'last_n', 'username', 'email', 'password'])
        except pd.errors.EmptyDataError:
            pd.DataFrame(columns=['first_n', 'last_n', 'username', 'email', 'password']).to_csv(CSV_FILE_PATH, index=False)

# Initialize CSV on startup
initialize_csv()

def update_user(first_n, last_n, username, email, password):
    if not all([first_n, last_n, username, email, password]):
        st.error('All fields are required.')
        return
    hashed_password = hash_data(password)
    hashed_email = hash_data(email)
    userinfo = pd.read_csv(CSV_FILE_PATH)
    if username in userinfo['username'].values:
        userinfo.loc[userinfo['username'] == username, ['first_n', 'last_n', 'email', 'password']] = [
            first_n, last_n, hashed_email, hashed_password
        ]
        st.success('User information updated successfully.')
    else:
        new_entry = pd.DataFrame([[first_n, last_n, username, hashed_email, hashed_password]],
                                 columns=['first_n', 'last_n', 'username', 'email', 'password'])
        userinfo = pd.concat([userinfo, new_entry], ignore_index=True)
        st.success('New user added successfully.')
    try:
        userinfo.to_csv(CSV_FILE_PATH, index=False)
    except PermissionError:
        st.error(f"Permission denied: Unable to write to {CSV_FILE_PATH}. Please check file permissions.")

def login_user(email, password):
    if not all([email, password]):
        st.error('Email and password are required.')
        return False
    userinfo = pd.read_csv(CSV_FILE_PATH)
    hashed_email = hash_data(email)
    hashed_password = hash_data(password)
    for _, row in userinfo.iterrows():
        if row['email'] == hashed_email and row['password'] == hashed_password:
            st.success('Login successful.')
            return True
    st.error('Invalid email or password.')
    return False

def signup_user(first_n, last_n, username, email, password):
    if not all([first_n, last_n, username, email, password]):
        st.error('All fields are required.')
        return
    hashed_password = hash_data(password)
    hashed_email = hash_data(email)
    userinfo = pd.read_csv(CSV_FILE_PATH)
    if username in userinfo['username'].values:
        st.error('Username already exists.')
    else:
        new_entry = pd.DataFrame([[first_n, last_n, username, hashed_email, hashed_password]],
                                 columns=['first_n', 'last_n', 'username', 'email', 'password'])
        userinfo = pd.concat([userinfo, new_entry], ignore_index=True)
        try:
            userinfo.to_csv(CSV_FILE_PATH, index=False)
            st.success('Signup successful.')
        except PermissionError:
            st.error(f"Permission denied: Unable to write to {CSV_FILE_PATH}. Please check file permissions.")

# Streamlit UI
st.title("User Authentication App")
menu = ["Login", "Signup", "Update"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Login":
    st.header("Login")
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
    if submit:
        if login_user(email, password):
            st.write("Welcome!")
elif choice == "Signup":
    st.header("Signup")
    with st.form("signup_form"):
        first_n = st.text_input("First Name")
        last_n = st.text_input("Last Name")
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Signup")
    if submit:
        signup_user(first_n, last_n, username, email, password)
elif choice == "Update":
    st.header("Update User Info")
    with st.form("update_form"):
        first_n = st.text_input("First Name")
        last_n = st.text_input("Last Name")
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Update")
    if submit:
        update_user(first_n, last_n, username, email, password)
