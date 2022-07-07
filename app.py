from flask import Flask, render_template, request, redirect


from add_user import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'real secret key'
db.init_app(app)


@app.route('/signup', methods=['POST', 'GET'])
def sign():
    id = request.form.get('login')
    password = request.form.get('password')

    if check_auth(id, password):
        return redirect('tasks')
    else:
        return render_template("sign.html")


@app.route('/tasks')
def tasks():
    return render_template("tasks.html")


if __name__ == "__main__":
    app.run(debug=True)
