from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Feedback
from forms import UserForm, LoginForm, FeedbackForm

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres:///feedback_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "secret123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)
toolbar = DebugToolbarExtension(app)

# db.drop_all()
db.create_all()


@app.route('/')
def show_home_page():
    """Redirects to registration screen."""
    return redirect('/register')


@app.route('/register', methods=['GET', 'POST'])
def registration_form():
    """Show and process registration form."""

    form = UserForm()
    if form.validate_on_submit():
        data = {k: v for k, v in form.data.items() if k != "csrf_token"}
        new_user = User.register(**data)
        db.session.add(new_user)
        db.session.commit()
        flash(f"{data['username']} added!", 'success')
        session['username'] = new_user.username
        return redirect(f"/users/{session['username']}")

    else:
        return render_template('registration.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_form():
    """Show and process login form."""

    form = LoginForm()
    if form.validate_on_submit():
        data = {k: v for k, v in form.data.items() if k != "csrf_token"}
        user = User.authenticate(**data)
        if user:
            flash(f"{data['username']} has logged in!", 'info')
            session['username'] = user.username
            return redirect(f"/users/{session['username']}")

        else:
            flash('The entered credentials are incorrect!', 'danger')

    return render_template('login.html', form=form)


@app.route('/users/<username>')
def show_secret_page(username):
    """Show page only visible to logged-in users."""

    if 'username' not in session:
        flash("You must be logged-in to access this resource.", 'danger')
        return redirect('/login')

    user = User.query.get_or_404(username)
    posts = Feedback.get_user_posts(username)
    if username == session['username']:
        form = FeedbackForm()
        return render_template('secret.html', user=user, posts=posts, form=form)

    else:
        return render_template('secret.html', user=user, posts=posts)


@app.route('/users/<username>/feedback/add', methods=['POST'])
def add_feedback(username):
    """Submit user feedback form."""

    if 'username' not in session:
        flash("You must be logged-in to access this resource.", 'danger')
        return redirect('/login')

    elif username != session['username']:
        flash("You do not have persmission to access this resource.", 'danger')
        return redirect(f"/users/{session['username']}")

    else:
        user = User.query.get_or_404(session['username'])
        form = FeedbackForm()
        if form.validate_on_submit():
            data = {k: v for k, v in form.data.items() if k != "csrf_token"}
            data['username'] = username
            new_feedback = Feedback(**data)
            db.session.add(new_feedback)
            db.session.commit()
            flash(f"{data['title']} added.", 'success')
            return redirect(f"/users/{session['username']}")
        else:
            return render_template('secret.html', user=user, form=form)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    """Log out user."""

    flash(f"{session['username']} has been logged out.", 'info')
    session.pop('username', None)
    return redirect('/login')


@app.route('/users/<username>/delete', methods=['POST'])
def delete_user(username):
    """Delete user."""

    if 'username' not in session:
        flash("You must be logged-in to access this resource.", 'danger')
        return redirect('/login')

    elif username != session['username']:
        flash("You do not have persmission to access this resource.", 'danger')
        return redirect(f"/users/{session['username']}")

    else:
        user = User.query.get_or_404(username)
        flash(f"{user.username} has been deleted.", 'info')
        db.session.delete(user)
        db.session.commit()
        session.pop('username', None)
        return redirect('/')


@app.route('/feedback/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    """Delete user."""

    if 'username' not in session:
        flash("You must be logged-in to access this resource.", 'danger')
        return redirect('/login')

    post = Feedback.query.get_or_404(post_id)
    if post.username != session['username']:
        flash("You do not have persmission to access this resource.", 'danger')
        return redirect(f"/users/{session['username']}")

    else:
        flash(f"{post.title} has been deleted.", 'info')
        db.session.delete(post)
        db.session.commit()
        return redirect(f"/users/{session['username']}")


@app.route('/feedback/<int:post_id>/edit', methods=['GET', 'POST'])
def edit_post(post_id):
    """Show edit post form and submit edit."""

    if 'username' not in session:
        flash("You must be logged-in to access this resource.", 'danger')
        return redirect('/login')

    post = Feedback.query.get_or_404(post_id)
    if post.username != session['username']:
        flash("You do not have persmission to access this resource.", 'danger')
        return redirect(f"/users/{session['username']}")

    else:
        form = FeedbackForm(obj=post)
        if form.validate_on_submit():
            post.title = form.title.data
            post.content = form.content.data
            db.session.commit()
            flash(f"{post.title} has been updated.", 'info')
            return redirect(f"/users/{session['username']}")
        else:
            return render_template('edit_post.html', form=form,post=post)
