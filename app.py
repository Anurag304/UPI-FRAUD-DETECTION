from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import joblib
import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Load the trained fraud detection model
model = joblib.load("rf_model.pkl")

# Function to connect to the database
def get_db_connection():
    conn = sqlite3.connect("users.db", check_same_thread=False)  # Fixes "database is locked" error
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return render_template('register.html.')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash("Login successful!", "success")
            return redirect(url_for('predict_page'))  # Redirect to predict page after login
        else:
            flash("Invalid username or password", "danger")

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", 
                           (username, email, hashed_password))
            conn.commit()
            conn.close()
            flash("Registration successful! You can now log in.", "success")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Username or Email already exists!", "danger")

    return render_template('register.html')

@app.route('/predict', methods=['GET', 'POST'])
def predict_page():
    if 'user_id' not in session:
        flash("Please log in to access this page.", "warning")
        return redirect(url_for('login'))

    prediction_result = None
    if request.method == 'POST':
        try:
            # Extract form data correctly
            trans_hour = float(request.form["trans_hour"])
            trans_day = float(request.form["trans_day"])
            trans_month = float(request.form["trans_month"])
            trans_year = float(request.form["trans_year"])
            trans_amount = float(request.form["trans_amount"])
            upi_number = request.form["upi_number"]  # Get UPI Number

            print(f"Received input: {trans_hour}, {trans_day}, {trans_month}, {trans_year}, {trans_amount}, {upi_number}")

            # Create DataFrame for prediction (Ensure UPI Number is included)
            df = pd.DataFrame([[trans_hour, trans_day, trans_month, trans_year, trans_amount, upi_number]],
                              columns=["trans_hour", "trans_day", "trans_month", "trans_year", "trans_amount", "upi_number"])

            # Check if the model works
            prediction = model.predict(df)
            print(f"Prediction Output: {prediction}")

            prediction_result = "Fraud Detected" if prediction[0] == 1 else "No Fraud"
            flash(f"Prediction: {prediction_result}", "success")

        except Exception as e:
            flash(f"Error in prediction: {e}", "danger")
            print(f"Error in prediction: {e}")

    return render_template('predict.html', result=prediction_result)

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
