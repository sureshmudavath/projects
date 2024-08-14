import os
import sys
import json
from datetime import datetime, timedelta
from bson import ObjectId
from pymongo import MongoClient
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, request, render_template, redirect, url_for, flash, session


### Load environment variables from .env file ###

load_dotenv()


### Instatiate flask app and configure necessary paramaters ###

app = Flask(__name__, static_url_path='', static_folder='static')
app.secret_key = os.getenv("FLASK_APP_SECRET").encode()
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)


### DATABASE CONNECTION ###

client = MongoClient(os.getenv('MONGODB_URI'))
db = client['library_management_system']

librarians = db['librarians']
patrons = db['patrons']
books = db['books']
bookings = db['bookings']


### COMMON ROUTES ###

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/about', methods=['GET'])
def about_us():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact_us():
    match request.method:
        case 'GET':
            return render_template('contact.html')
        case 'POST':
            try:
                name = request.form["name"]
                email = request.form["email"]
                message = request.form["message"]
                flash("Thanks for reaching out with us! Our support team will get back to you, soon...", "info")
                return redirect("/contact")
            except Exception as ex:
                flash(f"Unexpected exception triggered: {ex} | Contact us at: <support@libralink.io>", "error")
                return redirect("/contact")

@app.route('/login', methods=['GET', 'POST'])
def login_user():
    if "user_id" in session or "user_email" in session:
        flash("Continuing the logged-in session...", "info")
        return redirect(f"/{session['user_role']}/dashboard")

    match request.method:
        case 'GET':
            return render_template('login.html')
        case 'POST':
            try:
                email = request.form['email']
                _password = request.form['password']
                role = request.form['role']

                match role:
                    case 'librarian':
                        librarian = librarians.find_one(dict(email=email))
                        if not librarian:
                            flash(f"Please register! No record of the librarian exists.", "warning")
                            return redirect("/register")
                        if check_password_hash(librarian['password'], _password):
                            # Initialize session
                            session["user_id"] = str(librarian["_id"])
                            session["user_name"] = librarian["name"]
                            session["user_role"] = role
                            session["user_email"] = email
                            flash(f"Welcome to your librarian dashboard, {librarian['name']}!", "success")
                            return redirect("/librarian/dashboard")
                        flash(f"Invalid email or password! Please re-try.", "warning")
                        return redirect("/login")
                    case 'patron':
                        patron = patrons.find_one(dict(email=email))
                        if not patron:
                            flash(f"Please register! No record of the patron exists.", "warning")
                            return redirect("/register")
                        if check_password_hash(patron['password'], _password):
                            # Initialize session
                            session["user_id"] = str(patron["_id"])
                            session["user_name"] = patron["name"]
                            session["user_role"] = role
                            session["user_email"] = email
                            flash(f"Welcome to your patron dashboard, {patron['name']}!", "success")
                            return redirect("/patron/dashboard")
                        flash(f"Invalid email or password! Please re-try.", "warning")
                        return redirect("/login")
                    case _:
                        flash("Unsecure activity detected!", "error")
                        return redirect("/register")
            except Exception as ex:
                flash(f"ERROR: {ex}", "error")
                return redirect("/register")

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    if "user_id" in session or "user_email" in session:
        flash("Continuing the logged-in session...", "info")
        return redirect(f"/{session['user_role']}/dashboard")

    match request.method:
        case 'GET':
            return render_template('register.html')
        case 'POST':
            try:
                name = request.form['name']
                email = request.form['email']
                password = generate_password_hash(request.form['password'], method=os.getenv('HASH_METHOD'))
                phone = request.form['phone']
                institution = request.form['institution']
                role = request.form['role']

                match role:
                    case 'librarian':
                        if librarians.find_one(dict(email=email)):
                            flash(f"Registered librarian! Please login with <{email}>", "warning")
                            return redirect("/login")

                        _ = librarians.insert_one(dict(name=name, email=email, password=password,
                            phone=phone, institution=institution))
                    case 'patron':
                        if patrons.find_one(dict(email=email)):
                            flash(f"Registered patron! Please login with <{email}>", "warning")
                            return redirect("/login")

                        _ = patrons.insert_one(dict(name=name, email=email, password=password,
                            phone=phone, institution=institution))
                    case _:
                        flash("Unsecure activity detected!", "error")
                        return redirect("/register")
            except Exception as ex:
                flash(f"ERROR: {ex}", "error")
                return redirect("/register")

            flash(f"Registration successful! Please login, {name}.", "success")
            return redirect("/login")

@app.route('/forgot', methods=['GET', 'POST'])
def user_forgot_password():
    if "user_id" in session or "user_email" in session:
        flash("Continuing the logged-in session...", "info")
        return redirect(f"/{session['user_role']}/dashboard")

    match request.method:
        case 'GET':
            return render_template('forgot.html')
        case 'POST':
            try:
                email = request.form['email']
                role = request.form['role']

                match role:
                    case 'librarian':
                        librarian = librarians.find_one(dict(email=email))
                        if not librarian:
                            flash(f"Please register! No record of the librarian exists.", "warning")
                            return redirect("/register")
                    case 'patron':
                        patron = patrons.find_one(dict(email=email))
                        if not patron:
                            flash(f"Please register! No record of the patron exists.", "warning")
                            return redirect("/register")
                    case _:
                        flash("Unsecure activity detected! Report us, if this isn't from you.", "error")
                        return redirect("/contact")
            except Exception as ex:
                flash(f"ERROR: {ex} | REPORT US", "error")
                return redirect("/contact")

            flash("Our support team will reach out to you. Thanks for your patience!", "success")
            return redirect("/login")

@app.route('/logout', methods=['GET'])
def logout_user():
    if "user_id" not in session or "user_email" not in session:
        flash("Logged-out for security reasons! Please login again...", "error")
        return redirect("/login")

    # Log out user session
    session.pop("user_id", None)
    session.pop("user_name", None)
    session.pop("user_role", None)
    session.pop("user_email", None)
    flash("Session closed!", "info")
    return redirect("/login")

### LIBRARIAN ROUTES ###

@app.route('/librarian/dashboard', methods=['GET'])
def librarian_dashboard():
    if "user_id" not in session or "user_email" not in session or session["user_role"] != "librarian":
        flash("Access denied! Please login to continue...", "error")
        return redirect("/login")

    return render_template("librarian/dashboard.html", catalog=books.find(), str=str)

@app.route('/librarian/add/book', methods=['GET', 'POST'])
def add_book():
    if "user_id" not in session or "user_email" not in session or session["user_role"] != "librarian":
        flash("Access denied! Please login to continue...", "error")
        return redirect("/login")

    match request.method:
        case 'GET':
            return render_template("librarian/add_book.html")
        case 'POST':
            try:
                book_cover_url = request.form["book_cover_url"]
                title = request.form["title"]
                author = request.form["author"]
                genre = request.form["genre"]
                published = int(request.form["published"])

                # Check if the book is already listed in the catalog
                used_book_cover = books.find_one(dict(book_cover_url=book_cover_url))
                used_book_title = books.find_one(dict(title=title))

                warn_msg = "Book already listed! Please check the catalog."
                if used_book_cover:
                    warn_msg = f"Book cover already used for another book in the catalog with title <{used_book_cover['title']}>"

                if used_book_cover or used_book_title:
                    flash(warn_msg, "warning")
                    return redirect("/librarian/dashboard")

                _book = books.insert_one(dict(book_cover_url=book_cover_url, title=title, author=author,
                            genre=genre, published=published, librarian_id=ObjectId(session["user_id"])))
                flash(f"New book added: {_book.inserted_id}", "success")
                return redirect("/librarian/dashboard")
            except Exception as ex:
                flash(f"Unable to add book: {ex}", "error")
                return redirect("/librarian/dashboard")

@app.route('/librarian/edit/book/<book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    if "user_id" not in session or "user_email" not in session or session["user_role"] != "librarian":
        flash("Access denied! Please login to continue...", "error")
        return redirect("/login")

    match request.method:
        case 'GET':
            book_details = books.find_one({"_id": ObjectId(book_id)})
            return render_template("librarian/edit_book.html", book=book_details)
        case 'POST':
            try:
                book_cover_url = request.form["book_cover_url"]
                title = request.form["title"]
                author = request.form["author"]
                genre = request.form["genre"]
                published = int(request.form["published"])
                _book = books.update_one({"_id": ObjectId(book_id), "librarian_id": ObjectId(session["user_id"])},
                            {"$set": dict(book_cover_url=book_cover_url, title=title, author=author,
                            genre=genre, published=published, librarian_id=ObjectId(session["user_id"]))})
                flash(f"Book<{book_id}> updated!", "success")
                return redirect("/librarian/dashboard")
            except Exception as ex:
                flash(f"Unable to update book details: {ex}", "error")
                return redirect("/librarian/dashboard")


@app.route('/librarian/delete/book/<book_id>', methods=['GET'])
def delete_book(book_id):
    if "user_id" not in session or "user_email" not in session or session["user_role"] != "librarian":
        flash("Access denied! Please login to continue...", "error")
        return redirect("/login")

    try:
        _ = books.delete_one({"_id": ObjectId(book_id), "librarian_id": ObjectId(session["user_id"])})
        flash(f"Book<{book_id}> deleted!", "success")
        return redirect("/librarian/dashboard")
    except Exception as ex:
        flash(f"Unable to delete book details: {ex}", "error")
        return redirect("/librarian/dashboard")

@app.route('/librarian/available/books', methods=['GET'])
def librarian_available_books():
    if "user_id" not in session or "user_email" not in session or session["user_role"] != "librarian":
        flash("Access denied! Please login to continue...", "error")
        return redirect("/login")

    #available_books = books.find({"book_id": {"$nin": bookings.distinct("book_id")}})
    borrowed_book_ids = [b['book_id'] for b in bookings.find({"type": "borrow"}, {"book_id": 1, "_id": 0})]
    available_books = books.find({"_id": {"$nin": borrowed_book_ids}})
    return render_template("librarian/available_books.html", catalog=available_books)

@app.route('/librarian/borrows', methods=['GET'])
def book_borrows():
    if "user_id" not in session or "user_email" not in session or session["user_role"] != "librarian":
        flash("Access denied! Please login to continue...", "error")
        return redirect("/login")

    # Aggregation pipeline
    pipeline = [
        {
            '$lookup': {
                'from': 'books',  # collection to join
                'localField': 'book_id',  # field from the bookings collection
                'foreignField': '_id',  # field from the books collection
                'as': 'book_details'  # output array field
            }
        },
        {
            '$unwind': {
                'path': '$book_details',
                'preserveNullAndEmptyArrays': True  # to keep bookings even if no book details are found
            }
        }
    ]
    
    # Execute the aggregation pipeline
    booking_details = bookings.aggregate(pipeline)
    return render_template("librarian/borrows.html", catalog=booking_details, str=str)

@app.route('/librarian/returned/<booking_id>', methods=['GET'])
def mark_book_returned(booking_id):
    if "user_id" not in session or "user_email" not in session or session["user_role"] != "librarian":
        flash("Access denied! Please login to continue...", "error")
        return redirect("/login")

    try:
        _ = bookings.delete_one({"_id": ObjectId(booking_id)})
        flash(f"Booking marked as returned: <{booking_id}>", "success")
        return redirect("/librarian/dashboard")
    except Exception as ex:
        flash(f"Unable to mark book as returned details: {ex}", "error")
        return redirect("/librarian/dashboard")


@app.route('/librarian/profile', methods=['GET', 'POST'])
def librarian_profile():
    if "user_id" not in session or "user_email" not in session or session["user_role"] != "librarian":
        flash("Access denied! Please login to continue...", "error")
        return redirect("/login")

    match request.method:
        case 'GET':
            librarian = librarians.find_one(dict(_id=ObjectId(session["user_id"])))
            return render_template("librarian/profile.html", librarian=librarian)
        case 'POST':
            try:
                name = request.form["name"]
                phone = request.form["phone"]
                institution = request.form["institution"]
                _ = librarians.update_one({"_id": ObjectId(session["user_id"])},
                    {"$set": dict(name=name, phone=phone, institution=institution)})
                flash(f"Congratulations, {name}! Your profile updated successfully!", "success")
                return redirect("/librarian/dashboard")
            except Exception as ex:
                flash(f"Unable to update your profile: {ex}", "error")
                return redirect("/librarian/dashboard")

### PATRON ROUTES ###

@app.route('/patron/dashboard', methods=['GET'])
def patron_dashboard():
    if "user_id" not in session or "user_email" not in session or session["user_role"] != "patron":
        flash('Access denied! Please login to continue...', 'error')
        return redirect('/login')

    # Get all the available books for patron (which are not yet borrowed by others)
    borrowed_book_ids = [b['book_id'] for b in bookings.find({"type": "borrow"}, {"book_id": 1, "_id": 0})]
    available_books = books.find({"_id": {"$nin": borrowed_book_ids}})
    return render_template("patron/dashboard.html", catalog=available_books, str=str)

dates_overlap = lambda s1, e1, s2, e2: (s1 <= e2) and (e1 >= s2)

@app.route('/patron/borrow/<book_id>', methods=['GET', 'POST'])
def patron_borrow_book(book_id):
    if "user_id" not in session or "user_email" not in session or session["user_role"] != "patron":
        flash("Access denied! Please login to continue...", "error")
        return redirect("/login")

    match request.method:
        case 'GET':
            # Check bookings (not necessary, but for security reasons)
            if book_id in set(str(b["book_id"]) for b in bookings.find({"type": "borrow"}, {"book_id": 1, "_id": 0})):
                flash("Unfortunately borrowed by others. Please contact your librarian for more info!", "warning")
                return redirect("/patron/dashboard")
            book = books.find_one(dict(_id=ObjectId(book_id)))
            return render_template("patron/borrow_book.html", book=book, today=datetime.today().strftime('%Y-%m-%d'))
        case 'POST':
            try:
                checkin_date = datetime.strptime(request.form["checkin_date"], "%Y-%m-%d")
                checkout_date = datetime.strptime(request.form["checkout_date"], "%Y-%m-%d")

                # Validate <checkin_date> and <checkout_date>
                if checkin_date.date() != datetime.today().date() or checkin_date > checkout_date:
                    flash("Invalid checkin/checkout dates. Please refill the form!", "error")
                    return redirect(f'/patron/borrow/{book_id}')

                # Check for any reservation bookings
                reservations = list(bookings.find({"type": "reserve"}, {"book_id": 1, "checkin_date": 1, "checkout_date": 1, "_id": 0}))
                if book_id in set(str(b["book_id"]) for b in reservations):
                    reservations_dates = set((datetime.strptime(b["checkin_date"], "%Y-%m-%d"),
                        datetime.strptime(b["checkout_date"], "%Y-%m-%d")) for b in reservations)

                    if any(reservations_dates):
                        for (reservation_start, reservation_end) in reservations_dates:
                            if dates_overlap(checkin_date, checkout_date, reservation_start, reservation_end):
                                flash(f"Already reserved from {reservation_start.strftime('%Y-%m-%d')} to {reservation_end.strftime('%Y-%m-%d')}", "warning")
                                return redirect("/patron/dashboard")

                _booking = bookings.insert_one({
                        "book_id": ObjectId(book_id),
                        "patron_id": ObjectId(session["user_id"]),
                        "patron_name": session["user_name"],
                        "type": "borrow",
                        "checkin_date": checkin_date.strftime('%Y-%m-%d'),
                        "checkout_date": checkout_date.strftime('%Y-%m-%d')
                    })
                flash(f"Booking confirmed: {_booking.inserted_id}", "success")
                return redirect("/patron/dashboard")
            except Exception as ex:
                flash(f"Unable to offer booking on this book: {ex}", "error")
                return redirect("/patron/dashboard")

@app.route('/patron/reserve/<book_id>', methods=['GET', 'POST'])
def patron_reserve_book(book_id):
    if "user_id" not in session or "user_email" not in session or session["user_role"] != "patron":
        flash("Access denied! Please login to continue...", "error")
        return redirect("/login")

    match request.method:
        case 'GET':
            # Check bookings (not necessary, but for security reasons)
            if book_id in set(str(b["book_id"]) for b in bookings.find({"type": "borrow"}, {"book_id": 1, "_id": 0})):
                flash("Unfortunately borrowed by others. Please contact your librarian for more info!", "warning")
                return redirect("/patron/dashboard")
            book = books.find_one(dict(_id=ObjectId(book_id)))
            return render_template("patron/reserve_book.html", book=book)
        case 'POST':
            try:
                checkin_date = datetime.strptime(request.form["checkin_date"], "%Y-%m-%d")
                checkout_date = datetime.strptime(request.form["checkout_date"], "%Y-%m-%d")

                # Validate <checkin_date> and <checkout_date>
                if checkin_date.date() < datetime.today().date() or checkin_date > checkout_date:
                    flash("Invalid checkin/checkout dates. Please refill the form!", "error")
                    return redirect(f'/patron/borrow/{book_id}')

                # Check for any reservation bookings
                reservations = list(bookings.find({"type": "reserve"}, {"book_id": 1, "checkin_date": 1, "checkout_date": 1, "_id": 0}))
                if book_id in set(str(b["book_id"]) for b in reservations):
                    reservations_dates = set((datetime.strptime(b["checkin_date"], "%Y-%m-%d"),
                        datetime.strptime(b["checkout_date"], "%Y-%m-%d")) for b in reservations)

                    if any(reservations_dates):
                        for (reservation_start, reservation_end) in reservations_dates:
                            if dates_overlap(checkin_date, checkout_date, reservation_start, reservation_end):
                                flash(f"Already reserved from {reservation_start.strftime('%Y-%m-%d')} to {reservation_end.strftime('%Y-%m-%d')}", "warning")
                                return redirect("/patron/dashboard")

                _booking = bookings.insert_one({
                        "book_id": ObjectId(book_id),
                        "patron_id": ObjectId(session["user_id"]),
                        "patron_name": session["user_name"],
                        "type": "reserve",
                        "checkin_date": checkin_date.strftime('%Y-%m-%d'),
                        "checkout_date": checkout_date.strftime('%Y-%m-%d')
                    })
                flash(f"Booking confirmed: {_booking.inserted_id}", "success")
                return redirect("/patron/dashboard")
            except Exception as ex:
                flash(f"Unable to offer booking on this book: {ex}", "error")
                return redirect("/patron/dashboard")

@app.route('/patron/history', methods=['GET'])
def patron_recent_borrows_history():
    if "user_id" not in session or "user_email" not in session or session["user_role"] != "patron":
        flash("Access denied! Please login to continue...", "error")
        return redirect("/login")

    # Aggregation pipeline
    pipeline = [
        {
            '$match': {
                'patron_id': ObjectId(session['user_id']) # Filters documents by patron_id
            }
        },
        {
            '$lookup': {
                'from': 'books',  # collection to join
                'localField': 'book_id',  # field from the bookings collection
                'foreignField': '_id',  # field from the books collection
                'as': 'book_details'  # output array field
            }
        },
        {
            '$unwind': {
                'path': '$book_details',
                'preserveNullAndEmptyArrays': True  # to keep bookings even if no book details are found
            }
        }
    ]

    # Execute the aggregation pipeline
    booking_details = bookings.aggregate(pipeline)
    return render_template("patron/history.html", catalog=booking_details, str=str, dt=datetime)

@app.route('/patron/renew/<booking_id>/book/<book_id>', methods=['GET', 'POST'])
def patron_renew_booking(booking_id, book_id):
    if "user_id" not in session or "user_email" not in session or session["user_role"] != "patron":
        flash("Access denied! Please login to continue...", "error")
        return redirect("/login")

    match request.method:
        case 'GET':
            booking = bookings.find_one({"_id": ObjectId(booking_id)})
            book = books.find_one({"_id": ObjectId(book_id)})
            return render_template("patron/renew_book.html", booking=booking, book=book, str=str)
        case 'POST':
            try:
                booking = bookings.find_one({"_id": ObjectId(booking_id)})
                checkin_date = datetime.strptime(booking["checkin_date"], "%Y-%m-%d")
                old_checkout_date = datetime.strptime(booking["checkout_date"], "%Y-%m-%d")
                checkout_date = datetime.strptime(request.form["checkout_date"], "%Y-%m-%d")

                # Validate <checkin_date> and <checkout_date>
                if checkin_date > checkout_date:
                    flash(f"Invalid checkout date. Please refill the form!", "error")
                    return redirect(f'/patron/renew/{booking_id}/book/{book_id}')

                # Check for prepone mistake
                if old_checkout_date > checkout_date:
                    flash(f"Preponing a renew request? Please refill the form!", "error")
                    return redirect(f'/patron/renew/{booking_id}/book/{book_id}')

                # Check for any reservation bookings
                reservations = list(bookings.find({"type": "reserve"}, {"book_id": 1, "checkin_date": 1, "checkout_date": 1, "_id": 0}))
                if book_id in set(str(b["book_id"]) for b in reservations):
                    reservations_dates = set((datetime.strptime(b["checkin_date"], "%Y-%m-%d"),
                        datetime.strptime(b["checkout_date"], "%Y-%m-%d")) for b in reservations)

                    if any(reservations_dates):
                        for (reservation_start, reservation_end) in reservations_dates:
                            if dates_overlap(checkin_date, checkout_date, reservation_start, reservation_end):
                                flash(f"Already reserved from {reservation_start.strftime('%Y-%m-%d')} to {reservation_end.strftime('%Y-%m-%d')}", "warning")
                                return redirect(f"/patron/renew/{booking_id}/book/{book_id}")

                _booking = bookings.update_one(
                    {"_id": ObjectId(booking_id), "book_id": ObjectId(book_id)},
                    {"$set": {"checkout_date": checkout_date.strftime('%Y-%m-%d')}}
                )
                flash(f"Booking renewed: {booking_id}", "success")
                return redirect("/patron/history")
            except Exception as ex:
                flash(f"Unable to renew booking on this book: {ex}", "error")
                return redirect("/patron/history")

@app.route('/patron/pay_fine/<fine>/<booking_id>/book/<book_id>', methods=['GET', 'POST'])
def patron_pay_fine(fine, booking_id, book_id):
    if "user_id" not in session or "user_email" not in session or session["user_role"] != "patron":
        flash("Access denied! Please login to continue...", "error")
        return redirect("/login")

    match request.method:
        case 'GET':
            return render_template("patron/pay_fine.html", fine=fine, booking_id=booking_id, book_id=book_id)
        case 'POST':
            try:
                payment_method = request.form["payment_method"]
                card_name = request.form["card_name"]
                card_number = int(request.form["card_number"])
                card_exp_month = int(request.form["card_exp_month"])
                card_exp_year = int(request.form["card_exp_year"])
                cvv = int(request.form["cvv"])

                flash(f"Thank you for clearing the due fine amount: ${fine}. Please return the book immediately to avoid inconvenience to others! Keep Reading...", "success")
                return redirect("/patron/history")
            except Exception as ex:
                flash(f"Unable to pay due: {ex}", "error")
                return redirect("/patron/history")

@app.route('/patron/profile', methods=['GET', 'POST'])
def patron_profile():
    if "user_id" not in session or "user_email" not in session or session["user_role"] != "patron":
        flash("Access denied! Please login to continue...", "error")
        return redirect("/login")

    match request.method:
        case 'GET':
            patron = patrons.find_one(dict(_id=ObjectId(session["user_id"])))
            return render_template("patron/profile.html", patron=patron)
        case 'POST':
            try:
                name = request.form["name"]
                phone = request.form["phone"]
                institution = request.form["institution"]
                _ = patrons.update_one({"_id": ObjectId(session["user_id"])},
                    {"$set": dict(name=name, phone=phone, institution=institution)})
                flash(f"Congratulations, {name}! Your profile updated successfully!", "success")
                return redirect("/patron/dashboard")
            except Exception as ex:
                flash(f"Unable to update your profile: {ex}", "error")
                return redirect("/patron/dashboard")


### SCHEDULED JOBS ###


def _reservations_filter_():
    reservations = list(bookings.find({"type": "reserve"}, {"checkin_date": 1}))
    today = datetime.today().date()
    booking_ids = set(b['_id'] for b in reservations if datetime.strptime(b["checkin_date"], "%Y-%m-%d").date() == today)

    results = list()
    for booking_id in booking_ids:
        results.append(bookings.update_one({"_id": booking_id}, {"$set": {"type": "borrow"}}))

    log_filename = f"reservations_watchdog_{today.strftime('%Y_%m_%d')}.log"
    with open(file=log_filename, mode="a") as log_fhand:
        log_fhand.write("\n".join(map(lambda x: f"{x}", results)) + "\n")
    print(f"[EVENT LOG]: Reservations filtered! Result(s) logged at: {log_filename}")


if __name__ == "__main__":

    ### CRON JOB FUNCTION TO CHECK RESERVATIONS TODAY ###
    import atexit
    from sys import stderr, exit
    from apscheduler.schedulers.background import BackgroundScheduler

    _reservations_filter_() # RUN ON STARTUP (IN CASE OF ANY CRASHES)

    try:
        scheduler = BackgroundScheduler(daemon=True)
        scheduler.add_job(_reservations_filter_, "cron", hour=0, minute=0)
        scheduler.start()
        atexit.register(lambda: scheduler.shutdown())
    except Exception as ex:
        print(f"[ERROR]: {ex}", file=stderr)
        exit(1)

    #####################################################

    app.run(debug=True)
