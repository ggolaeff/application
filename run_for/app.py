from datetime import datetime, timedelta

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


@app.route('/', methods=['GET'])
def main_page():
    return redirect(url_for('sign'))


@app.route('/signup', methods=['POST', 'GET'])
def sign():
    id = request.form.get('login')
    password = request.form.get('password')

    if check_auth(id, password):
        login_user(load_user(id))
        session[str(id)] = id
        session['kd'] = datetime.now()
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
    id_ping = Tasks.id_ping
    max_id = 0
    task_elev = {}
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
    deadline_list = [0] * (max_id + 1)
    task_list = [0] * (max_id + 1)
    for task in tasks:
        if task.end_date:
            deadline_list[task.id] = str(task.end_date - datetime.now()).replace(' days ', ':')
        user_task = Users.query.filter_by(id=task.from_user_id).first()
        nmUser = user_task.name
        task_list[task.id] = nmUser

    tasks_all = []
    if role == 0:
        for task in tasks:
            if task.id_ping != 1:
                tasks_all.append(task)
    else:
        for task in tasks:
            if task.id_ping != 2:
                tasks_all.append(task)
    for task in tasks_all:
        task_elev[task] = task.elevations
    task_elev_list = []
    sorted_tuple = sorted(task_elev.items(), key=lambda x: x[1])
    task_elev = dict(sorted_tuple)
    for task in task_elev.keys():
        task_elev_list.append(task)
    task_elev_list.reverse()
    status_filter = request.form.get('filter')
    if status_filter != None:
        tasks_filtered = []
        for task in task_elev_list:
            if status_filter == "nonecheck" and task.status == "Не прочитана":
                tasks_filtered.append(task)
            elif status_filter == "read" and task.status == "Прочитана":
                tasks_filtered.append(task)
            elif status_filter == "looking" and task.status == "На рассмотрении":
                tasks_filtered.append(task)
            elif status_filter == "good" and task.status == "Зачтена":
                tasks_filtered.append(task)
            elif status_filter == "bad" and task.status == "Не зачтена":
                tasks_filtered.append(task)
        task_elev_list = tasks_filtered
    return render_template("tasks.html",
                           name_user=name_user,
                           role=role,
                           tasks=task_elev_list,
                           task_list=task_list,
                           deadline_list=deadline_list,
                           session=session,
                           id_ping=id_ping
                           # elevations=elevations
                           )


# Упорядочивание задач по статусу:
# Tasks.query.order_by(Tasks.status).all()
# [<Tasks status ="не прочитана">, <Tasks status="в архиве">, <Tasks status="в обработке">,
# <Tasks status="оценка выставлена">]
#
# '0' == 'задача ни у кого не удалена'
# '1' == 'удалена у студента'
# '2' == 'удалена у преподавателя'
# '3' == 'удалить у студента и преподователя(кнопка от студента)'
# if tasks = Tasks.query.filter_by(id_ping=3).first()
# for task in tasks:
#     db.session.delete(tasks)
#     db.session.commit()
# '4' == 'в архиве у препода'
# if tasks = Tasks.query.filter_by(id_ping=4).first()
# for task in tasks:
#   if role == 0:
# '5' == 'в архиве у студента'
# '6' == 'в архиве у обоих'
# for task in tasks:
#   if id_ping = 5
#
# '7' == ''
# '8' == ''
# '9' == ''
# status = 0 - описание задачи из архива(Прочитана, не прочитана, в архиве)
# elevations = 0 - Поднятие задачи в списке
# id_ping = 0 - это числовое значние статуса(

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
                         text_task=text_task, files=files, begin_date=begin_date, status="Не прочитана", end_date=end_date,
                         id_ping=0, elevations=0)
            db.session.add(task)
            db.session.commit()
        return redirect('tasks')
    except AttributeError:

        return render_template("add_task.html", names=names)


@app.route('/view_task', methods=['GET', 'POST'])
@login_required
def view_task():
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
        tasks = Tasks.query.filter_by(from_user_id=session['_user_id']).all()
        for task in tasks:
            if max_id < task.id:
                max_id = task.id

    task_id = int(str(request.url).replace('http://127.0.0.1:5000/view_task?', '').replace('=', ''))
    task = Tasks.query.filter_by(id=task_id).first()

    name_task = task.name_task
    text_task = task.text_task
    files = task.files
    status = task.status
    status_now = request.form.get('status')
    if status == "Не прочитана" and status_now == None:
        task.status = "Прочитана"
        db.session.commit()
    elif status_now != None:
        if status_now == "looking":
            task.status = "На рассмотрении"
            db.session.commit()
        if status_now == "good":
            task.status = "Зачтена"
            db.session.commit()
        if status_now == "bad":
            task.status = "Не зачтена"
            db.session.commit()

    from_user = Users.query.filter_by(id=task.from_user_id).first()
    to_user = Users.query.filter_by(id=task.to_user_id).first()
    from_user_contact = from_user.contact
    to_user_contact = to_user.contact
    from_user_name = from_user.name
    delete_status = request.form.get('del')

    if delete_status == "all":
        db.session.delete(task)
        db.session.commit()
        return redirect('tasks')
    if delete_status == "one" and role == 0 and task.id_ping == 2:
        db.session.delete(task)
        db.session.commit()
        return redirect('tasks')
    elif delete_status == "one" and role == 0:
        task.id_ping = 1
        db.session.commit()
        return redirect('tasks')
    if delete_status == "one" and role == 1 and task.id_ping == 1:
        db.session.delete(task)
        db.session.commit()
        return redirect('tasks')
    elif delete_status == "one" and role == 1:
        task.id_ping = 2
        db.session.commit()
        return redirect('tasks')
    elev = request.form.get('elev')
    if elev == '1' and session['kd'].replace(tzinfo=None)-datetime.now() < timedelta(0):
        begin_kd = datetime.now()
        end_date = begin_kd + timedelta(minutes=3)
        session['kd'] = end_date
        task.elevations += 1
        db.session.commit()
    if session['kd'].replace(tzinfo=None) -datetime.now() < timedelta(0):
        time_lost = "0 cek."
    else:
        delta = session['kd'].replace(tzinfo=None)-datetime.now()
        if delta > timedelta(minutes=1):
            time_lost = f"{delta.seconds} cek."
        else:
            time_lost = f"{delta.seconds} сек."
    return render_template("view_task.html",
                           name_task=name_task,
                           text_task=text_task,
                           files=files,
                           status=status,
                           from_user_contact=from_user_contact,
                           to_user_contact=to_user_contact,
                           from_user_name=from_user_name,
                           name_user=name_user,
                           role=role,
                           time_lost=time_lost
                           )


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('sign'))


# @app.route('/tasks')
# @login_required
# def delete():
#     for task in tasks:
#         if task.id_ping == 3:  # '3' == 'удалить у студента и преподователя(кнопка от студента)'
#             task.status = "удалить у студента и преподователя(кнопка от студента)"
#             db.session.commit()


if __name__ == "__main__":
    app.run(debug=True)

    from task_edit import db

    db.create_all()