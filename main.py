from flask import Blueprint, session, render_template

import users

main = Blueprint("main", __name__)

@main.route("/")
def index():
    return render_template("index.html")

@main.route("/dashboard")
@users.logged_in
@users.has_membership
def dashboard(user):
    return "This page is kinda empty."