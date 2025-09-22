from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# -------------------- DATABASE CONNECTION --------------------
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        return conn
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None

# -------------------- AUTHENTICATION --------------------
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'], method='sha256')
        role = request.form['role']

        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                    (username, password, role)
                )
                conn.commit()
                flash("User registered successfully!", "success")
                return redirect(url_for('login_user'))
            except Error as e:
                flash(f"Error: {e}", "danger")
            finally:
                cursor.close()
                conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
                user = cursor.fetchone()
                if user and check_password_hash(user['password'], password):
                    session['user_id'] = user['id']
                    session['role'] = user['role']
                    flash("Login successful!", "success")
                    return redirect(url_for('dashboard'))
                else:
                    flash("Invalid username or password", "danger")
            except Error as e:
                flash(f"Error: {e}", "danger")
            finally:
                cursor.close()
                conn.close()
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully", "success")
    return redirect(url_for('login_user'))

# -------------------- DASHBOARD --------------------
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login_user'))
    return render_template('dashboard.html', role=session['role'])

# -------------------- RELIEFCENTERS --------------------
@app.route('/reliefcenters')
def reliefcenters():
    conn = get_db_connection()
    data = []
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM reliefcenters")
            data = cursor.fetchall()
        except Error as e:
            flash(f"Error: {e}", "danger")
        finally:
            cursor.close()
            conn.close()
    return render_template('reliefcenters.html', centers=data)

# -------------------- VOLUNTEERS --------------------
@app.route('/volunteers')
def volunteers():
    conn = get_db_connection()
    data = []
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM volunteers")
            data = cursor.fetchall()
        except Error as e:
            flash(f"Error: {e}", "danger")
        finally:
            cursor.close()
            conn.close()
    return render_template('volunteers.html', volunteers=data)

# -------------------- VICTIMS --------------------
@app.route('/victims')
def victims():
    conn = get_db_connection()
    data = []
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT v.*, r.name AS center_name 
                FROM victims v 
                LEFT JOIN reliefcenters r ON v.assigned_center_id = r.id
            """)
            data = cursor.fetchall()
        except Error as e:
            flash(f"Error: {e}", "danger")
        finally:
            cursor.close()
            conn.close()
    return render_template('victims.html', victims=data)

# -------------------- DONATIONS --------------------
@app.route('/donations', methods=['GET', 'POST'])
def donations():
    conn = get_db_connection()
    data = []

    if request.method == 'POST':
        donor_name = request.form['donor_name']
        type_ = request.form['type']
        amount = request.form.get('amount') or None
        item_name = request.form.get('item_name') or None
        quantity = request.form.get('quantity') or None
        center_id = request.form['center_id']

        if type_ == 'Money':
            quantity = None
        else:
            quantity = int(quantity) if quantity else 1

        if type_ == 'Money':
            amount = float(amount) if amount else 0.0
        else:
            amount = None

        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO donations (donor_name, type, amount, item_name, quantity, center_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (donor_name, type_, amount, item_name, quantity, center_id))
            conn.commit()
            flash("Donation added successfully!", "success")
        except Error as e:
            flash(f"Error: {e}", "danger")
        finally:
            cursor.close()

    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT d.*, r.name AS center_name 
                FROM donations d 
                LEFT JOIN reliefcenters r ON d.center_id = r.id
            """)
            data = cursor.fetchall()
        except Error as e:
            flash(f"Error: {e}", "danger")
        finally:
            cursor.close()
            conn.close()
    return render_template('donations.html', donations=data)

# -------------------- SUPPLIES --------------------
@app.route('/supplies')
def supplies():
    conn = get_db_connection()
    data = []
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT s.*, r.name AS center_name 
                FROM supplies s 
                LEFT JOIN reliefcenters r ON s.center_id = r.id
            """)
            data = cursor.fetchall()
        except Error as e:
            flash(f"Error: {e}", "danger")
        finally:
            cursor.close()
            conn.close()
    return render_template('supplies.html', supplies=data)

# -------------------- ALERTS --------------------
@app.route('/alerts')
def alerts():
    conn = get_db_connection()
    data = []
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT a.*, r.name AS center_name 
                FROM alerts a 
                LEFT JOIN reliefcenters r ON a.center_id = r.id
            """)
            data = cursor.fetchall()
        except Error as e:
            flash(f"Error: {e}", "danger")
        finally:
            cursor.close()
            conn.close()
    return render_template('alerts.html', alerts=data)

# -------------------- CHECK ALL TABLES --------------------
@app.route('/check_all', methods=['GET'])
def check_all():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    tables = ['reliefcenters', 'volunteers', 'victims', 'donations', 'supplies']
    result = {}
    
    for table in tables:
        cursor.execute(f"SELECT * FROM {table}")
        result[table] = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return jsonify(result)

# -------------------- RUN APP --------------------
if __name__ == '__main__':
    app.run(debug=True)
