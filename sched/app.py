from flask import Flask
from flask import abort, jsonify, redirect, render_template, request, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, current_user
from flask.ext.login import login_user, logout_user

from sched import filters
from sched.forms import AppointmentForm, LoginForm
from sched.models import Appointment, Base
from sched.models import User


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sched.db'
app.config['SECRET_KEY'] = 'enydM2ANhdcoKwdVa0jWvEsbPFuQpMjf'

db = SQLAlchemy(app)
db.Model = Base

filters.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated():
        return redirect(url_for('appointment_list'))
    form = LoginForm(request.form)
    error = None
    if request.method == 'POST' and form.validate():
        email = form.username.data.lower().strip()
        password = form.password.data.lower().strip()
        user, authenticated = User.authenticate(db.session.query, email, password)
        if authenticated:
            login_user(user)
            return redirect(url_for('appointment_list'))
        else:
            error = 'Incorrect username or password.'
    return render_template('user/login.html', form=form, error=error)

@app.route('/logout/')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.errorhandler(404)
def error_not_found(error):
    return render_template('error/not_found.html'), 404


@app.route('/appointments/')
def appointment_list():
    """Provide HTML listing of all appointments."""
    # Query: Get all Appointment objects, sorted by date
    appts = (db.session.query(Appointment)).order_by(Appointment.start.asc()).all()
    return render_template('appointment/index.html', appts=appts)


@app.route('/appointments/<int:appointment_id>/')
def appointment_detail(appointment_id):
    """Provide HTML pgage with a given appointment."""
    appt = db.session.query(Appointment).get(appointment_id)
    if appt is None:
        abort(404)
    return render_template('appointment/detail.html', appt=appt)


@app.route('/appointments/create/', methods=['GET', 'POST'])
def appointment_create():
    """Provide HTML form to create a new appointment."""
    form = AppointmentForm(request.form)
    if request.method == 'POST' and form.validate():
        appt = Appointment()
        form.populate_obj(appt)
        db.session.add(appt)
        db.session.commit()
        # Success. Send user back to full appointment list.
        return redirect(url_for('appointment_list'))
    return render_template('appointment/edit.html', form=form)


@app.route('/appointments/<int:appointment_id>/edit/', methods=['GET', 'POST'])
def appointment_edit(appointment_id):
    """Provide HTML form to edit a given appointment."""
    appt = db.session.query(Appointment).get(appointment_id)
    if appt is None:
        abort(404)
    form = AppointmentForm(request.form, appt)
    if request.method == 'POST' and form.validate():
        form.populate_obj(appt)
        db.session.commit()
        # Success. Send the user back to the detail view.
        return redirect(url_for('appointment_detail', appointment_id=appt.id))
    return render_template('appointment/edit.html', form=form)


@app.route('/appointments/<int:appointment_id>/delete/', methods=['DELETE'])
def appointment_delete(appointment_id):
    """Delete record using HTTP DELETE, response with JSON"""
    appt = db.session.query(Appointment).get(appointment_id)
    if appt is None:
        # Abort with Not Found, but with simple JSON response
        response = jsonify({'status': 'Not Found'})
        response.status_code = 404
        return response
    db.session.delete(appt)
    db.session.commit()
    return jsonify({'status': 'OK'})


