from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from datetime import datetime
from werkzeug.utils import secure_filename
import cv2
import numpy as np
from PIL import Image
import sqlite3

app = Flask(__name__) 
app.secret_key = "plantdoctor_secret"
UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
     os.makedirs(UPLOAD_FOLDER)

# ---------- Database Setup ----------
conn = sqlite3.connect('database.db')
c = conn.cursor()
c.execute('''CREATE TABLE  IF NOT EXISTS users
             (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, email TEXT UNIQUE, password TEXT)''')
c.execute('''CREATE TABLE I F NOT EXISTS history
             (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, file_path TEXT,
             plant_name TEXT, plant_age TEXT, disease TEXT, cause TEXT,
             treatment TEXT, affected_ratio REAL, save_prob TEXT, user_note TEXT,
             timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
conn.commit()
conn.close()

# ---------- Detection Function ----------
def detect_disease(image_path):
    image = cv2.imread(image_path)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # Simple brown/yellow detection
    brown_lower = np.array([10, 100, 20])
    brown_upper = np.array([35, 255, 255])
    mask = cv2.inRange(hsv, brown_lower, brown_upper)
    ratio = (cv2.countNonZero(mask) / (image.size / 3)) * 100

    if ratio > 15:
        disease = "Leaf is  diseased"
        cause = "Possible heat stress or lack of water"
        treatment = "Provide water, shade, and check pesticides"
        save_prob = "70%"
        color = (0, 0, 255)
    else:
        disease = "Healthy Leaf"
        cause = "No issues"
        treatment = "Normal care"
        save_prob = "95%"
        color = (0, 255, 0)

    # Overlay text on image
    cv2.putText(image, f"{disease} ({ratio:.1f}%)", (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, color, 3)
    result_path = os.path.join(UPLOAD_FOLDER, "result_" + os.path.basename(image_path))
    cv2.imwrite(result_path, image)

    # For demo, plant name and age are static
    plant_name = "Tomato"
    plant_age = "2 months"

    return plant_name, plant_age, disease, cause, treatment, ratio, save_prob, result_path

# ---------- Routes ----------

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('home'))
    return redirect(url_for('login'))

# ---- Login ----
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT id, username FROM users WHERE email=? AND password=?", (email, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            return redirect(url_for('home'))
        else:
            flash("Invalid credentials")
    return render_template('login.html')

# ---- Register ----
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        try:
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                      (username, email, password))
            conn.commit()
            conn.close()
            flash("Account created! Please login.")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Email already registered")
    return render_template('register.html')

 # ---- Logout ----
@app.route('/logout')
def logout():
    session.clear()
     return redirect(url_for('login'))

# ---- Home ----
@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('home.html', user=session['username'])

# ---- Upload Page ----
@app.route('/upload_page')
def upload_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('upload_page.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    file = request.files['file']
    user_note = request.form.get('user_note')
    if file:
        filename = datetime.now().strftime("%Y%m%d_%H%M%S_") + secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        plant_name, plant_age, disease, cause, treatment, ratio, save_prob, result_image = detect_disease(filepath)
        # Save history
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('''INSERT INTO history (user_id, file_path, plant_name, plant_age, disease, cause, treatment,
                     affected_ratio, save_prob, user_note) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (session['user_id'], result_image, plant_name, plant_age, disease, cause, treatment,
                   ratio, save_prob, user_note))
        conn.commit()
        conn.close()
        return render_template('result.html', plant_name=plant_name, plant_age=plant_age, disease=disease,
                               cause=cause, treatment=treatment, affected_ratio=ratio,
                               save_prob=save_prob, result_image=result_image, user_note=user_note)
    return "No file uploaded", 400

# ---- Capture Page ----
@app.route('/capture_page')
def capture_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('capture_page.html')

@app.route('/capture', methods=['POST'])
def capture():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    file = request.files['file']
    user_note = request.form.get('user_note')
    if file:
        filename = datetime.now().strftime("%Y%m%d_%H%M%S_capture.jpg")
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        plant_name, plant_age, disease, cause, treatment, ratio, save_prob, result_image = detect_disease(filepath)
        # Save history
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('''INSERT INTO history (user_id, file_path, plant_name, plant_age, disease, cause, treatment,
                     affected_ratio, save_prob, user_note) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (session['user_id'], result_image, plant_name, plant_age, disease, cause, treatment,
                   ratio, save_prob, user_note))
        conn.commit()
        conn.close()
        return render_template('result.html', plant_name=plant_name, plant_age=plant_age, disease=disease,
                               cause=cause, treatment=treatment, affected_ratio=ratio,
                               save_prob=save_prob, result_image=result_image, user_note=user_note)
    return "No file captured", 400

# ---- History Page ----
@app.route('/history')
def history():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT file_path, plant_name, plant_age, disease, cause, treatment, affected_ratio, save_prob, user_note, timestamp FROM history WHERE user_id=? ORDER BY timestamp DESC", (session['user_id'],))
    rows = c.fetchall()
    conn.close()
    return render_template('history.html', history=rows)

# ---- About Page ----
@app.route('/about')
def about():
    return render_template('about.html',
                           developer="Sathishkumar",
                           project="Plant Doctor",
                           description="Detect diseases and stress in plants online",
                           email="sathishkumarsk2210@gmail.com",
                           credit="Open Source")

# ---- Run App ----
if __name__ == '__main__':
    app.run(debug=True)



