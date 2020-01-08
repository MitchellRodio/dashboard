from flask import Flask

import database as db

from auth import auth

app = Flask(__name__)

app.register_blueprint(auth)

@app.route("/ping")
def ping():
    return "pong"

if __name__ == "__main__":
    app.run(debug=True)