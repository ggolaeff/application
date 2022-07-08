from datetime import datetime

from flask import render_template, request, redirect, session
from flask_login import login_required, login_user


from add_user import *
from task_edit import *

db.init_app(app)

n = 1

@app.route('/signup', methods=['POST', 'GET'])
def sign():

    id = request.form.get('login')
    password = request.form.get('password')

    if check_auth(id, password):
        login_user(load_user(id))
        session[str(id)] = id
        return redirect('tasks')
    else:
        return render_template("sign.html")


@app.route('/tasks', methods=['GET', 'POST'])
@login_required
def tasks():

    return render_template("tasks.html")


@app.route('/add_tasks', methods=['GET', 'POST'])
@login_required
def add_task():
    global n
    names = []
    users = Users.query.filter(Users.id).all()
    for user in range(len(users)):
        if users[user].role == 1:
            names.append(users[user].name)
    id_task = n
    name_tasks = request.form.get('name')
    from_user_id = int(session['_user_id'])
    to_user_id = request.form.get('to_user')
    text_task = request.form.get('text_task')
    files = request.form.get('files')
    begin_date = datetime.now()
    end_date = request.form.get('end_date')

    task = Tasks(id=id_task, name_task=name_tasks, from_user_id=from_user_id, to_user_id=to_user_id, text_task=text_task, files=files, begin_date=begin_date, end_date=end_date)
    n += 1
    db.session.add(task)
    db.session.commit()
    return redirect('tasks')





if __name__ == "__main__":
    app.run(debug=True)
