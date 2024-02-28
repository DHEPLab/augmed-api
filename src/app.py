from flask import Flask

from src.task.controller.controller import hello_blueprint

app = Flask(__name__)

app.register_blueprint(hello_blueprint)

if __name__ == '__main__':
    app.run()
