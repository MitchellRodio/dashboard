from flask import Blueprint, session

import users

main = Blueprint("main", __name__)

@main.route("/")
def index():
    return str(session.get("logged_in"))

@main.route("/dashboard")
@users.logged_in
@users.has_membership
def dashboard(user):
    return "This page is kinda empty."