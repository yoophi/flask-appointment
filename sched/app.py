from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask import render_template

from sched.models import Base

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sched.db'

db = SQLAlchemy(app)
db.Model = Base


@app.route('/')
def index():
    return render_template('index.html')
