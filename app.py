from flask import Flask, render_template, redirect, url_for, request

app = Flask(__name__)


# TODO change the route here from "/" to "/quiz builder" whenever we have a real landing page, right now it only exist as a way to actually test the flask 
@app.route('/', methods=['GET', 'POST'])
def quiz_builder():
    if request.method == 'POST':
        print('worked')
    return render_template("quiz_builder.html")