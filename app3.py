from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

# -----------------------------
# DATABASE PATH
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "notes.db")

app = Flask(__name__)
app.secret_key = "secret123"


# -----------------------------
# INIT DATABASE
# -----------------------------
def init_db():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, content TEXT)")
    conn.commit()
    conn.close()


# 🔥 IMPORTANT: Call DB init here (outside main)
init_db()


# -----------------------------
# HOME
# -----------------------------
@app.route("/")
def home():
    if "user_id" in session:
        return redirect("/dashboard")
    return redirect("/login")


# -----------------------------
# REGISTER
# -----------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")


# -----------------------------
# LOGIN
# -----------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session["user_id"] = user[0]
            return redirect("/dashboard")

    return render_template("login.html")


# -----------------------------
# DASHBOARD
# -----------------------------
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT * FROM notes WHERE user_id=?", (session["user_id"],))
    notes = c.fetchall()
    conn.close()

    return render_template("dashboard.html", notes=notes)


# -----------------------------
# ADD NOTE
# -----------------------------
@app.route("/add", methods=["POST"])
def add():
    if "user_id" not in session:
        return redirect("/login")

    content = request.form["content"]

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("INSERT INTO notes (user_id, content) VALUES (?, ?)", (session["user_id"], content))
    conn.commit()
    conn.close()

    return redirect("/dashboard")


# -----------------------------
# DELETE NOTE
# -----------------------------
@app.route("/delete/<int:id>")
def delete(id):
    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("DELETE FROM notes WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/dashboard")


# -----------------------------
# LOGOUT
# -----------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# -----------------------------
# RUN (Local only)
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)