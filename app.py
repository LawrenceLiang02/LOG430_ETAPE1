"""This module does something"""
from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
    """Test method"""
    return "Hello, World!"


def create_app():
    """Method for tests"""
    return app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
