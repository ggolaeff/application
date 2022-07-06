from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), primary_key=False)
    email = db.Column(db.String(100), primary_key=False)
    role = db.Column(db.Integer, primary_key=False)
    password = db.Column(db.String(100), primary_key=False)

    def __repr__(self):
        return '<Users %r>' % self.id

@app.route('/signup')
def sign():
    return render_template("sign.html")


if __name__ == "__main__":
    app.run(debug=True)
