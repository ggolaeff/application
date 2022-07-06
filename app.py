from flask import Flask, render_template

app = Flask(__name__)


@app.route('/signup')
def sign():
    return render_template("sign.html")


if __name__ == "__main__":
    app.run(debug=True)