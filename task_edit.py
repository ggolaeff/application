from flask_sqlalchemy import SQLAlchemy

from add_user import db


class Tasks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_task = db.Column(db.String(100), primary_key=False)
    from_user_id = db.Column(db.Integer, primary_key=False)
    to_user_id = db.Column(db.Integer, primary_key=False)
    text_task = db.Column(db.Text, primary_key=False)
    files = db.Column(db.Text, primary_key=False)
    begin_date = db.Column(db.DateTime, primary_key=False)
    end_date = db.Column(db.DateTime, primary_key=False)

    def __repr__(self):
        return '<Tack %r>' % self.id



