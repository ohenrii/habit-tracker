# Habit Tracker

#### Video Demo: https://youtu.be/UulUSPubC2w?si=vwtfX1TJWtVbz5lX

## Description

This project is a **Habit Tracker** developed as the final project for **CS50**. The application allows users to create an account, log in, and track daily habits by recording completions, viewing statistics, and maintaining a history of progress over time.

The main goal of the project is to apply, in a practical way, the concepts taught throughout the course, such as web development with Flask. The system was designed to be simple and easy to use.

Each user has their own habits, completely isolated from other users. For each habit, it is possible to mark daily completion, undo that action, view detailed statistics, and track streaks, which helps encourage long-term consistency.

## Features

- User registration with data validation
- Login and logout with session management
- Secure password hashing
- Creation of custom habits
- Editing and deletion of habits
- Daily habit completion tracking
- Ability to undo habit completion
- Count of habits completed in the last 7 days
- Detailed statistics per habit
- Completion percentage calculation
- Current streak calculation
- Maximum streak calculation
- Protection of routes for authenticated users

## Technologies Used

- **Python 3**
- **Flask**
- **SQLite**
- **HTML / CSS**
- **Bootstrap**

## Project Structure

### app.py

Main Flask application file. It contains all route logic, authentication, database interactions, and habit statistics calculations. Its main responsibilities include:

- Session management with Flask-Session
- User registration and login
- Full CRUD operations for habits
- Marking and unmarking habit completions
- Calculation of statistics such as streaks and completion percentage
- Route protection through authentication

### helpers.py

Auxiliary functions file. It contains the `login_required` decorator, inspired by CS50 examples, which prevents access to protected routes when the user is not authenticated.

### Database (habits.db)

The database uses SQLite and contains the following tables:

- **users**: stores registered users, including username and password hash
- **habits**: stores habits created by users
- **completions**: stores the dates on which each habit was completed

Each table was designed to ensure data integrity and guarantee that users can only access their own information.

### templates/

Contains HTML templates rendered with Jinja2:

- `layout.html`: base template with navbar and flash messages
- `login.html`: login form
- `register.html`: registration form
- `habits.html`: main page displaying the list of habits
- `edit_habit.html`: habit editing page
- `habit_stats.html`: detailed statistics for a habit

### static/

I chose not to use a custom CSS file because Bootstrap fully met the current design needs of the application.

## Design Decisions

Habit statistics such as streaks and completion percentage were implemented manually to demonstrate custom logic and understanding of date manipulation. Some SQL queries and calculations were developed with the help of AI, always reviewed and adapted to properly fit the project’s requirements.

The interface was intentionally kept simple using Bootstrap, prioritizing clarity and usability.

## Security

- Passwords are never stored in plain text; all are securely hashed
- Sessions are used for authentication
- Sensitive routes are protected with `login_required`
- Every action validates the `user_id`, preventing access to other users’ data
- Sensitive variables, such as `SECRET_KEY`, are stored in a `.env` file

## Possible Future Improvements

- Progress charts over time
- Habit tracking by period (weekly/monthly)
- Automatic reminders

## Conclusion

This project allowed me to apply in practice the main concepts learned in CS50, such as web development with Flask, SQL databases, authentication, and session management. The Habit Tracker meets its proposed goals by providing a functional solution for habit tracking and serves as a solid foundation for future improvements.
