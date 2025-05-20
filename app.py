from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello, World!"

# Pour permettre les tests
def create_app():
    return app

if __name__ == "__main__":
    app.run(debug=True)