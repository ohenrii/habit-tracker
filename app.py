import os
from datetime import date, timedelta

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
    return redirect("/habits")


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


@app.route("/logout")
def logout():

    session.clear()
    flash("You have been logged out", "success")
    return redirect("/login")


@app.route("/habits", methods=["GET", "POST"])
@login_required
def habits():

    user_id = session["user_id"]

    if request.method == "POST":

        name = request.form.get("name")
        name = name.strip()

        if not name:
            flash("It's necessary to provide the name of the habit", "danger")
            return redirect("/habits")

        try:
            db.execute(
                "INSERT INTO habits (user_id, name) VALUES (?, ?)", user_id, name
            )

            flash(f"Habit '{name}' successfully created!", "success")
            return redirect("/habits")

        except Exception as e:
            flash("Error while creating habit. Try again", "danger")
            return redirect("/habits")

    habits = db.execute(
        "SELECT id, name, created_at FROM habits WHERE user_id = ? ORDER BY created_at DESC",
        user_id,
    )

    # iso format sugested by AI
    today = date.today().isoformat()

    # query loop created with help of AI to show how many days of the week a habit was completed
    for habit in habits:
        week_count = db.execute(
            """SELECT COUNT(*) as count FROM completions 
                WHERE habit_id = ? 
                AND completed_date >= date('now', '-7 days')""",
            habit["id"],
        )
        habit["week_count"] = week_count[0]["count"]

        # query created with help of AI
        completed_today = db.execute(
            "SELECT * FROM completions WHERE habit_id = ? AND completed_date = ?",
            habit["id"],
            today,
        )
        habit["completed_today"] = len(completed_today) > 0

    return render_template("habits.html", habits=habits)


@app.route("/habits/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit_habit(id):

    habit = db.execute(
        "SELECT * FROM habits WHERE id = ? AND user_id = ?", id, session["user_id"]
    )

    if not habit:
        flash("Habit not found or access denied", "danger")
        return redirect("/habits")

    habit = habit[0]

    if request.method == "POST":

        name = request.form.get("name")
        description = request.form.get("description")

        if not name:
            flash("The name of the habit is mandatory", "danger")
            return redirect(f"/habits/{id}/edit")

        db.execute(
            "UPDATE habits SET name = ?, description = ? WHERE id = ?",
            name,
            description,
            id,
        )

        flash(f"Habit '{name}' updated successfully", "success")

        return redirect("/habits")

    else:
        return render_template("edit_habit.html", habit=habit)


@app.route("/habits/<int:id>/delete", methods=["POST"])
@login_required
def delete_habit(id):

    habit = db.execute(
        "SELECT * FROM habits WHERE id = ? AND user_id = ?", id, session["user_id"]
    )

    if not habit:
        flash("Habit not found or access denied", "danger")
        return redirect("/habits")

    habit_name = habit[0]["name"]

    db.execute("DELETE FROM habits WHERE id = ?", id)

    flash(f"Habit '{habit_name}' successfully deleted", "success")

    return redirect("/habits")


@app.route("/habits/<int:id>/check", methods=["POST"])
@login_required
def check_habit(id):

    habit = db.execute(
        "SELECT * FROM habits WHERE id = ? AND user_id = ?", id, session["user_id"]
    )

    if not habit:
        flash("Habit not found or access denied", "danger")
        return redirect("/habits")

    habit_name = habit[0]["name"]

    # isoformat sugested by AI
    today = date.today().isoformat()

    existing = db.execute(
        "SELECT * FROM completions WHERE habit_id = ? AND completed_date = ?", id, today
    )

    if existing:
        flash(f"You already marked '{habit_name}' as done today", "warning")
        return redirect("/habits")

    db.execute(
        "INSERT INTO completions (habit_id, completed_date) VALUES (?, ?)", id, today
    )

    flash(f"Great! Habit '{habit_name}' marked as done", "success")

    return redirect("/habits")


@app.route("/habits/<int:id>/uncheck", methods=["POST"])
@login_required
def uncheck_habit(id):
    user_id = session["user_id"]

    habit = db.execute(
        "SELECT id, name FROM habits WHERE id = ? AND user_id = ?", id, user_id
    )

    habit_name = habit[0]["name"]

    if not habit:
        flash("Habit not found", "danger")
        return redirect("/habits")

    db.execute(
        "DELETE FROM completions WHERE habit_id = ? AND completed_date = date('now')",
        id,
    )

    flash(f"Habit '{habit_name}' unchecked for today", "success")
    return redirect("/habits")


@app.route("/habits/<int:id>/stats", methods=["GET"])
@login_required
def habit_stats(id):

    user_id = session["user_id"]

    habit_rows = db.execute(
        "SELECT id, name, description, created_at FROM habits WHERE id = ? AND user_id = ?",
        id,
        user_id,
    )

    if not habit_rows:
        flash("Habit not found", "danger")
        return redirect("/habits")

    habit = habit_rows[0]

    # query created with hepl of AI
    days_completed = db.execute(
        "SELECT COUNT(*) AS count FROM completions WHERE habit_id = ?", id
    )[0]["count"]

    created_date = date.fromisoformat(habit["created_at"][:10])
    days_since_creation = (date.today() - created_date).days + 1

    # logic of how to calculate conclusion percentage created with help of AI
    if days_since_creation > 0:
        completion_percentage = round((days_completed / days_since_creation) * 100, 1)
    else:
        completion_percentage = 0

    completion_rows = db.execute(
        "SELECT completed_date FROM completions WHERE habit_id = ? ORDER BY completed_date ASC",
        id,
    )

    # variable created ny AI
    completion_dates = [
        date.fromisoformat(row["completed_date"]) for row in completion_rows
    ]

    current_streak = 0
    today = date.today()

    while today in completion_dates:
        current_streak += 1
        today -= timedelta(days=1)

    max_streak = 0
    streak = 0
    previous_day = None

    # loop created with help of AI
    for d in completion_dates:
        if previous_day and d == previous_day + timedelta(days=1):
            streak += 1
        else:
            streak = 1
        max_streak = max(max_streak, streak)
        previous_day = d

    return render_template(
        "habit_stats.html",
        habit=habit,
        days_completed=days_completed,
        days_since_creation=days_since_creation,
        completion_percentage=completion_percentage,
        current_streak=current_streak,
        max_streak=max_streak,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
