import smtplib
import os
import random
import sqlite3
import joblib
import logging
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv  # For secure credentials
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Flask App Setup
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "your_secret_key")  # Secure key for session management

# Load the trained fraud detection model
model = joblib.load("rf_model.pkl")

# Database Connection Function
def get_db_connection():
    conn = sqlite3.connect("users.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# Function to generate OTP
def generate_otp():
    return str(random.randint(100000, 999999))

# Function to send OTP via Email
def send_email(subject, body, recipient_email):
    logging.info("📧 Sending OTP via email...")

    smtp_server = "smtp.gmail.com"
    port = 587
    username = os.getenv("EMAIL_USER")  # Use environment variables
    password = os.getenv("EMAIL_PASS")  # Use app password for security

    if not username or not password:
        logging.error("❌ Email credentials missing. Check .env file.")
        return False

    msg = MIMEMultipart()
    msg['From'] = username
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()
        server.login(username, password)
        server.sendmail(username, recipient_email, msg.as_string())
        server.quit()
        logging.info("✅ OTP sent successfully via email.")
        return True
    except Exception as e:
        logging.error(f"❌ Email Error: {e}")
        return False

@app.route('/')
def home():
    return render_template('register.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if not username or not email or not password:
            flash("All fields are required!", "warning")
            return render_template("register.html")

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


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        otp = request.form.get("otp")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if not user:
            flash("Invalid username or password!", "danger")
            return render_template("login.html")

        # Step 1: Verify Password First
        if not session.get("otp_sent"):
            if not check_password_hash(user["password"], password):
                flash("Invalid username or password!", "danger")
                return render_template("login.html")

            email = user["email"]
            generated_otp = generate_otp()
            
            session["otp"] = generated_otp
            session["otp_sent"] = True
            session["otp_attempts"] = 0
            session["otp_expiry"] = (datetime.now() + timedelta(minutes=5)).timestamp()  # Expire after 5 mins

            email_body = f"<h3>Your OTP is: <b>{generated_otp}</b></h3>"
            send_email("Your Login OTP", email_body, email)
            flash("OTP sent to your registered email.", "info")
            return render_template("login.html")

        # Step 2: Verify OTP
        if otp:
            # Check if OTP expired
            if datetime.now().timestamp() > session.get("otp_expiry", 0):
                flash("OTP expired! Please request a new one.", "danger")
                session.pop("otp", None)
                session.pop("otp_sent", None)
                return redirect(url_for("login"))

            if otp == session.get("otp"):
                session["user_id"] = user["id"]
                session.pop("otp", None)
                session.pop("otp_sent", None)
                session.pop("otp_expiry", None)

                flash("Login successful!", "success")
                return redirect(url_for("homeDeashboard"))
            else:
                session["otp_attempts"] += 1
                if session["otp_attempts"] >= 3:
                    session.pop("otp", None)
                    session.pop("otp_sent", None)
                    flash("Too many failed attempts. Please request a new OTP.", "danger")
                else:
                    flash("Invalid OTP! Try again.", "danger")
    session.pop("otp_sent", None)
    return render_template("login.html")

@app.route('/homeDeashboard')
def homeDeashboard():
    print(session) 
    print("xyz")   
    if 'user_id' not in session:
        flash("Please log in to access this page.", "warning")
        return render_template("login.html")
    return render_template("index.html")

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))


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



if __name__ == '__main__':
    app.run(debug=True)
