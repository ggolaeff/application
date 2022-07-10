from flask import flash, Flask, g
from flask_login import UserMixin, LoginManager
from flask_sqlalchemy import SQLAlchemy

from werkzeug.security import check_password_hash


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///applic.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'real secret key'
db = SQLAlchemy(app)
manager = LoginManager(app)


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), primary_key=False)
    email = db.Column(db.String(100), primary_key=False)
    role = db.Column(db.Integer, primary_key=False)
    password = db.Column(db.String(100), primary_key=False)

    def __repr__(self):
        return '<Users %r>' % self.id


class Sessions(db.Model):
    id_user = db.Column(db.Integer, primary_key=True)
    begin_session = db.Column(db.DateTime, primary_key=False)
    end_session = db.Column(db.DateTime, primary_key=False)

    def __repr__(self):
        return '<Session %r>' % self.id_user


@manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)


def check_auth(login, password):
    check = Users.query.filter(Users.id == login).all()
    g.id = login
    if not check:
        flash('Неврный логин')
        return False
    else:
        if check_password_hash(check[0].password, password):
            return True
        else:
            flash('Неврный пароль')
            return False