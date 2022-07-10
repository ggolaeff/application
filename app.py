from datetime import datetime

from flask import render_template, request, redirect, session, url_for, flash
from flask_login import login_required, login_user, logout_user

from add_user import *
from task_edit import *

db.init_app(app)

n = 8


def reformat_datetime(string):
    datetime_list = []
    num = ''
    for i in string:
        if i.isdigit():
            num += i
        else:
            num = int(num)
            datetime_list.append(num)
            num = ''
    num = int(num)
    datetime_list.append(num)
    return datetime_list


@app.route('/signup', methods=['POST', 'GET'])
def sign():
    id = request.form.get('login')
    password = request.form.get('password')

    if check_auth(id, password):
        login_user(load_user(id))
        session[str(id)] = id
        session['contact'] = load_user(id).contact
        return redirect('tasks')
    else:
        return render_template("sign.html")


@app.route('/tasks', methods=['GET', 'POST'])
@login_required
def tasks():
    user = Users.query.filter_by(id=session['_user_id']).first()
    role = user.role
    name_user = user.name
    max_id = 0
    if role == 0:
        tasks = Tasks.query.filter_by(from_user_id=session['_user_id']).all()
        for task in tasks:
            if max_id < task.id:
                max_id = task.id
    else:
        tasks = Tasks.query.filter_by(to_user_id=session['_user_id']).all()
        for task in tasks:
            if max_id < task.id:
                max_id = task.id
    deadline_list = [0] * (max_id+1)
    task_list = [0] * (max_id+1)
    for task in tasks:
        if task.end_date:
            deadline_list[task.id] = str(task.end_date-datetime.now()).replace(' days ', ':')
        user_task = Users.query.filter_by(id=task.from_user_id).first()
        nmUser = user_task.name
        task_list[task.id] = nmUser

    return render_template("tasks.html",
                           name_user=name_user,
                           role=role,
                           tasks=tasks,
                           task_list=task_list,
                           deadline_list=deadline_list,
                           session=session
                           )


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = Users.query.filter_by(id=session['_user_id']).first()
    contact_begin = session['contact']
    role = user.role
    name_user = user.name

    if role == 0:
        role = 'Студент'
    else:
        role = 'Преподаватель'
    check_contact = request.form.get('check_contact')
    contact = request.form.get(f'{check_contact}_text')
    if request.method == "POST" and contact != None and check_contact != None:
        user.contact = contact
        db.session.commit()
        session['contact'] = contact
        return redirect('profile')
    elif request.method == "POST":
        last_password = request.form.get('last_password')
        new_password = request.form.get('new_password')
        rep_new_password = request.form.get('rep_new_password')
        if check_auth(user.id, last_password):
            if new_password == rep_new_password:
                create_new_password(user, new_password)
                flash('Пароль изменен')
                return redirect('profile')
            else:
                flash('Пароли не совпадают')
        else:
            flash('Неверный пароль')
    return render_template("profile.html",
                           name_user=name_user,
                           role=role,
                           begin_contact=contact_begin
                           )


@app.route('/add_tasks', methods=['GET', 'POST'])
@login_required
def add_task():
    global n
    names = ['...']
    users = Users.query.filter(Users.id).all()
    for user in range(len(users)):
        if users[user].role == 1:
            names.append(users[user].name)

    id_task = n
    while Tasks.query.filter(Tasks.id == id_task).first() is not None:
        id_task += 1
    name_tasks = request.form.get('name')
    from_user_id = int(session['_user_id'])
    to_name = request.form.get('to_user')
    text_task = request.form.get('text_task')
    files = request.form.get('files')
    begin_date = datetime.now()
    end_date = request.form.get('end_date')

    try:
        to_user_id = Users.query.filter_by(name=to_name).first()
        to_user_id = to_user_id.id
        try:
            end_date = datetime(year=reformat_datetime(end_date)[0], month=reformat_datetime(end_date)[1],
                                day=reformat_datetime(end_date)[2], hour=reformat_datetime(end_date)[3],
                                minute=reformat_datetime(end_date)[4])
        except ValueError:
            end_date = None
        if name_tasks == '' or text_task == '':
            flash("Заполните поля")
            return render_template("add_task.html", names=names)
        else:
            task = Tasks(id=id_task, name_task=name_tasks, from_user_id=from_user_id, to_user_id=to_user_id,
                         text_task=text_task, files=files, begin_date=begin_date, end_date=end_date, status="Не прочитана")
            db.session.add(task)
            db.session.commit()
        return redirect('tasks')
    except AttributeError:

        return render_template("add_task.html", names=names)


@app.route('/view_task', methods=['GET', 'POST'])
@login_required
def view_task():
    task_id = int(str(request.url).replace('http://127.0.0.1:5000/view_task?', '').replace('=', ''))
    task = Tasks.query.filter_by(id=task_id).first()
    name_task = task.name_task
    text_task = task.text_task
    files = task.files
    status = task.status

    from_user = Users.query.filter_by(id=task.from_user_id).first()
    to_user = Users.query.filter_by(id=task.to_user_id).first()
    from_user_contact = from_user.contact
    to_user_contact = to_user.contact
    from_user_name = from_user.name

    return render_template("view_task.html",
                           name_task=name_task,
                           text_task=text_task,
                           files=files,
                           status=status,
                           from_user_contact=from_user_contact,
                           to_user_contact=to_user_contact,
                           from_user_name=from_user_name
                           )


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('sign'))


if __name__ == "__main__":
    app.run(debug=True)