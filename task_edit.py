from flask_sqlalchemy import SQLAlchemy

from add_user import app

db_task = SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


class Tasks(db_task.Model):
    id = db_task.Column(db_task.Integer, primary_key=True)
    from_user_id = db_task.Column(db_task.Integer, primary_key=False)
    to_user_id = db_task.Column(db_task.Integer, primary_key=False)
    text_task = db_task.Column(db_task.Text, primary_key=False)
    files = db_task.Column(db_task.Text, primary_key=False)

    def __repr__(self):
        return '<Tack %r>' % self.id



