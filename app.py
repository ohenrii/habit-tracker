import os

from cs50 import SQL
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash

from flask_session import Session
from helpers import login_required

app = Flask(__name__)

load_dotenv()
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///habits.db")


@app.route("/")
@login_required
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if session.get("user_id"):
        return redirect("/")

    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username")
    password = request.form.get("password")

    if not username:
        flash("Username is required", "danger")
        return redirect("/login")

    if not password:
        flash("Password is required", "danger")
        return redirect("/login")

    rows = db.execute("SELECT * FROM users WHERE username = ?", username)

    if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
        flash("Incorrect username or password", "danger")
        return redirect("/login")

    session["user_id"] = rows[0]["id"]

    flash(f"Welcome back, {username}!", "success")

    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():

    if session.get("user_id"):
        return redirect("/")

    if request.method == "GET":
        return render_template("register.html")

    username = request.form.get("username")
    password = request.form.get("password")
    confirmation = request.form.get("confirmation")

    if not username:
        flash("Username is required", "danger")
        return redirect("/register")

    if not password:
        flash("Password is required.", "danger")
        return redirect("/register")

    if not confirmation:
        flash("Password confirmation is required", "danger")
        return redirect("/register")

    if password != confirmation:
        flash("Passwords don't match", "danger")
        return redirect("/register")

    user_exists = db.execute("SELECT * FROM users WHERE username = ?", username)

    if user_exists:
        flash("Username already taken. Please choose another", "danger")
        return redirect("/register")

    password_hash = generate_password_hash(password)

    try:
        user_id = db.execute(
            "INSERT INTO users (username, hash) VALUES (?, ?)",
            username,
            password_hash,
        )

        session["user_id"] = user_id

        flash(f"Welcome, {username}! Account created successfully", "success")

        return redirect("/")

    except Exception as e:
        flash("Error creating account. Please try again", "danger")
        return redirect("/register")


@app.route("/logout", methods=["GET", "POST"])
def logout():

    if not session.get("user_id"):
        return redirect("/login")

    session.clear()
    flash("You have been logged out", "success")
    return redirect("/login")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
