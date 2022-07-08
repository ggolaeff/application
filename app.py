from flask import Flask, render_template, request, redirect
from flask_login import login_required, login_user

from add_user import *
#from task_edit import *

db.init_app(app)


@app.route('/signup', methods=['POST', 'GET'])
def sign():
    id = request.form.get('login')
    password = request.form.get('password')

    if check_auth(id, password):
        login_user(load_user(id))
        return redirect('tasks')
    else:
        return render_template("sign.html")


@app.route('/tasks', methods=['GET', 'POST'])
@login_required
def tasks():

    return render_template("tasks.html")


@app.route('/add_tasks')
@login_required
def add_task():
    return render_template("add_task.html")


if __name__ == "__main__":
    app.run(debug=True)
