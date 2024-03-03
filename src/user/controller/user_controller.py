from flask import Blueprint
from src.user.service.user_service import get_hello_message

hello_blueprint = Blueprint('hello_blueprint', __name__)

@hello_blueprint.route('/hello')
def hello_world():
    return get_hello_message()