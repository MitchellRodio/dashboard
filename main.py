from flask import Blueprint, session, render_template, redirect, url_for

import users

main = Blueprint("main", __name__)

@main.route("/")
def index():
    return render_template("index.html")

@main.route("/dashboard")
@users.logged_in
@users.has_membership
def dashboard(user):
    return render_template("dashboard.html", user=user, display_user=users.DisplayUser.from_session())

@main.route("/reset")
@users.logged_in
@users.has_membership
def reset_login_key(user):
    user.set_login_key()
    return redirect(url_for("main.dashboard"))