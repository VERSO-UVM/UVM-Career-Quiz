from flask import Flask, request, render_template, redirect, url_for, session
import sqlite3
import log_in



app = Flask(__name__)


@app.route("/")
def quizz_builder():
    return render_template("quizz_builder.html")