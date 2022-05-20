import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')
#@bp.route associates the URL /register with the register view function.
@bp.route('/register', methods=('GET', 'POST'))
def register():
    #If the user submitted the form, request.method will be 'POST'. In this case, start validating the input.
    if request.method == 'POST':
        #request.form is a special type of dict mapping submitted form keys and values. The user will input their username and password.
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        
        #db.execute takes a SQL query with ? placeholders for any user input, and a tuple of values to replace the placeholders with.
        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    #generate_password_hash() is used to securely hash the password, and that hash is stored.
                    (username, generate_password_hash(password)),
                )
                #db.commit() needs to be called afterwards to save the changes.
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                #After storing the user, they are redirected to the login page. url_for() generates the URL for the login view based on its name.
                #This is preferable to writing the URL directly as it allows you to change the URL later without changing all code that links to it. 
                #redirect() generates a redirect response to the generated URL.
                return redirect(url_for("auth.login"))

        #flash() stores messages that can be retrieved when rendering the template.
        flash(error)

    return render_template('auth/register.html')
#render_template() will render a template containing the HTML
@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        #fetchone() returns one row from the query. If the query returned no results, it returns None.
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            #session is a dict that stores data across requests.
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')
    
#bp.before_app_request() registers a function that runs before the view function, no matter what URL is requested.
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view