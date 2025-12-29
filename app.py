from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash

from flask_session import Session
from helpers import login_required

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///habits.db")


@app.route("/")
def index():
    if "user_id" not in session:
        return redirect("/login")

    return render_template("index.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

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

        if existing_user:
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

    else:
        return render_template("register.html")


if __name__ == "__main__":
    app.run(debug=True)
