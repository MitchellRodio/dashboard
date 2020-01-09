from flask import Flask

import database as db
from auth import auth

import string
import random

app = Flask(__name__)

app.register_blueprint(auth)

secret_key = "".join(random.choice(string.printable) for _ in range(32))
app.secret_key = secret_key
print(f"Booting up with secret key {secret_key}")

@app.route("/ping")
def ping():
    return "pong"

if __name__ == "__main__":
    app.run(debug=True)