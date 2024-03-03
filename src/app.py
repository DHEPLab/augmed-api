from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from src.config import Config  # Update this path as necessary

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

@app.route('/')
def hello():
    return "Hello, World!"

if __name__ == '__main__':
    app.run(debug=True)
