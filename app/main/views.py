from flask import redirect,send_file
from . import main
import os



@main.route('/',methods=['GET'])
def index():
	return send_file(os.path.join('static','index.html'))

