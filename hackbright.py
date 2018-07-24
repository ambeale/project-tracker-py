"""Hackbright Project Tracker.

A front-end for a database that allows users to work with students, class
projects, and the grades students receive in class projects.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy()


def connect_to_db(app):
    """Connect the database to our Flask app."""

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///hackbright'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


def get_student_by_github(github):
    """Given a GitHub account name, print info about the matching student."""

    QUERY = """
        SELECT first_name, last_name, github
        FROM students
        WHERE github = :github
        """

    db_cursor = db.session.execute(QUERY, {'github': github})

    row = db_cursor.fetchone()

    print("Student: {} {}\nGitHub account: {}".format(row[0], row[1], row[2]))


def make_new_student(first_name, last_name, github):
    """Add a new student and print confirmation.

    Given a first name, last name, and GitHub account, add student to the
    database and print a confirmation message.
    """
    
    sql = """
        INSERT INTO students (first_name, last_name, github)
        VALUES (:fname, :lname, :github)
        """

    db.session.execute(sql, { 'fname': first_name,
                              'lname': last_name,
                              'github': github })

    db.session.commit()

    print("Successfully added student: {} {}.".format(first_name, last_name))


def get_project_by_title(title):
    """Given a project title, print information about the project."""
    
    QUERY = """
        SELECT title, description, max_grade
        FROM projects
        WHERE title = :title
        """

    cursor = db.session.execute(QUERY, {'title' : title })

    project_info = cursor.fetchone()

    output = "Project Title: {}\nProject Description: {}\nMax Grade: {}"

    print(output.format(project_info[0], 
                        project_info[1],
                        project_info[2]))


def get_grade_by_github_title(github, title):
    """Print grade student received for a project."""
    
    QUERY = """
        SELECT grade
        FROM grades
        WHERE student_github = :github AND project_title = :title
        """

    cursor = db.session.execute(QUERY, {'github' : github,
                                        'title': title})

    student_grade = cursor.fetchone()

    if student_grade:
        print("Grade received on {}: {}".format(title, student_grade[0]))

    else:
        print("No grade recorded.")



def assign_grade(github, title, grade):
    """Assign a student a grade on an assignment and print a confirmation."""
    
    QUERY = """
        SELECT max_grade
        FROM projects
        WHERE title = :gtitle
        """

    grade_cursor = db.session.execute(QUERY, { 'gtitle' : title })

    max_grade = grade_cursor.fetchone()
    max_grade = int(max_grade[0])

    if int(grade) > max_grade:
        print("Invalid grade. Max grade is {}".format(max_grade))

    else:
        sql = """
            INSERT INTO grades (student_github, project_title, grade)
            VALUES (:sgithub, :ptitle, :sgrade)
            """

        db.session.execute(sql, { 'sgithub' : github,
            'ptitle' : title,
            'sgrade' : grade })

        db.session.commit()

        print("Grade for {} has been recorded.".format(title))


def handle_input():
    """Main loop.

    Repeatedly prompt for commands, performing them, until 'quit' is received
    as a command.
    """

    command = None

    while command != "quit":
        input_string = input("Welcome to the HBA Database!\nHere are the available commands:\nstudent\nnew_student\nsearch_project\nget_grade\nassign_grade\nquit\n>> ")
        tokens = input_string.split()
        command = tokens[0]
        args = tokens[1:]

        if command == "student":
            github = args[0]
            get_student_by_github(github)

        elif command == "new_student":
            first_name, last_name, github = args  # unpack!
            make_new_student(first_name, last_name, github)

        elif command == "search_project":
            project_title = args[0]
            get_project_by_title(project_title)

        elif command == "get_grade":
            github, title = args
            get_grade_by_github_title(github, title)

        elif command == "assign_grade":
            github, title, grade = args
            assign_grade(github, title, grade)

        else:
            if command != "quit":
                print("Invalid Entry. Try again.")


if __name__ == "__main__":
    connect_to_db(app)

    handle_input()

    # To be tidy, we close our database connection -- though,
    # since this is where our program ends, we'd quit anyway.

    db.session.close()
