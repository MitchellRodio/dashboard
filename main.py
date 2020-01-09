from flask import Blueprint, session

main = Blueprint("main", __name__)

@main.route("/")
def index():
    return str(session.get("logged_in"))