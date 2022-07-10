from add_user import db


class Tasks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_task = db.Column(db.String(100), primary_key=False)
    from_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    to_user_id = db.Column(db.Integer, primary_key=False)
    text_task = db.Column(db.Text, primary_key=False)
    files = db.Column(db.Text, primary_key=False)
    begin_date = db.Column(db.DateTime, primary_key=False)
    end_date = db.Column(db.DateTime, primary_key=False)
    status = db.Column(db.String(100), primary_key=False)

    def __repr__(self):
        return '<Task %r>' % self.id



