import json
from flask import Flask, render_template, request, redirect, url_for, flash
import os
app = Flask(__name__)
app.secret_key = "secret"
USERS_FILE = "users.json"
WORKS_FILE = "works.json"
# Ensure works.json exists
if not os.path.exists(WORKS_FILE):
    with open(WORKS_FILE, "w") as f:
        json.dump([], f)  # Start with an empty list

# Load users from JSON file
def load_users():
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Save users to JSON file
def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)
        #class&home assign saves


def load_works():
    try:
        with open(WORKS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_works(works):
    with open(WORKS_FILE, "w") as f:
        json.dump(works, f, indent=4)


# Home page
@app.route('/')
def index():
    return render_template('index.html')
# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    users = load_users()
    error_message = None

    if request.method == 'POST':
        phone = request.form.get('phone')
        password = request.form.get('password')

        if phone not in users:
            # Phone not registered
            error_message = "Phone number not registered!"
        else:
            user = users[phone]
            if user["password"] != password:
                # Wrong password
                error_message = "Incorrect password!"
            else:
                # Login successful
                flash(f"Welcome {user['fullname']}!", "success")
                return redirect(url_for('dashboard', phone=phone))

    # Render login page with the error message (if any)
    return render_template('login.html', error=error_message)



# Signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    users = load_users()
    if request.method == 'POST':
        fullname = request.form.get('fullname')
        Grade = request.form.get('Grade')
        Section = request.form.get('Section')
        SEX = request.form.get('SEX')
        phone = request.form.get('phone')
        password = request.form.get('password')

        if phone in users:
            flash("Phone number already registered!", "error")
            return redirect(url_for('signup'))

        users[phone] = {"fullname": fullname,"Grade":Grade, "Section":Section, "SEX":SEX, "phone": phone, "password": password}
        save_users(users)
        flash("Account created successfully! Please login.", "success")
        return redirect(url_for('login'))

    return render_template('signup.html')


# Dashboard after login
@app.route('/dashboard/<phone>')
def dashboard(phone):
    users = load_users()
    user = users.get(phone)  # Only logged-in student
    if not user:
        flash("User not found!", "error")
        return redirect(url_for('login'))

    works = load_works()
    # Filter works ONLY for this student's grade and section
    student_works = [w for w in works if w["grade"] == user["Grade"] and w["section"] == user["Section"]]

    # Count works per type
    counts = {
        "classwork": sum(1 for w in student_works if w["type"]=="classwork"),
        "homework": sum(1 for w in student_works if w["type"]=="homework"),
        "assignment": sum(1 for w in student_works if w["type"]=="assignment")
    }

    # Pass user info and filtered works to template
    return render_template('dashboard.html', user=user, counts=counts, works=student_works)
    #all
@app.route('/api/work_counts/<phone>')
def api_work_counts(phone):
    users = load_users()
    user = users.get(phone)
    if not user:
        return {"classwork":0, "homework":0, "assignment":0}

    works = load_works()
    student_works = [w for w in works if w["grade"] == user["Grade"] and w["section"] == user["Section"]]

    counts = {
        "classwork": sum(1 for w in student_works if w["type"]=="classwork"),
        "homework": sum(1 for w in student_works if w["type"]=="homework"),
        "assignment": sum(1 for w in student_works if w["type"]=="assignment")
    }
    return counts


    #teacher htmls
@app.route('/teacher', methods=['GET', 'POST'])
def teacher():
    works = load_works()
    if request.method == 'POST':
        type_ = request.form.get('type')
        grade = request.form.get('grade')
        section = request.form.get('section')
        question = request.form.get('question')

        works.append({
            "type": type_,
            "grade": grade,
            "section": section,
            "question": question
        })
        save_works(works)
        flash(f"{type_.capitalize()} posted successfully!", "success")
        return redirect(url_for('teacher'))

    return render_template('teacher.html', works=works)



    #admin page it show all password's
@app.route('/admin')
def admin():
    users = load_users()  # Load all users from JSON
    return render_template('admin.html', users=users)
# API: get all works
@app.route('/api/works', methods=['GET'])
def api_get_works():
    return load_works()   # returns the JSON list


# API: post new work
@app.route('/api/works', methods=['POST'])
def api_post_work():
    data = request.get_json()

    if not data:
        return {"error": "Invalid data"}, 400

    works = load_works()
    works.append({
        "type": data.get("type"),
        "grade": data.get("grade"),
        "section": data.get("section"),
        "question": data.get("question")
    })
    save_works(works)

    return {"message": "Work saved successfully!"}, 201



if __name__ == "__main__":
    app.run(debug=True)
