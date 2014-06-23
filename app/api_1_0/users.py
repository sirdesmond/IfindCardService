from flask import jsonify,request,make_response,send_file,url_for
from . import api
from ..models import User
from ..errors import unauthorized
import os

static_folder = '/app/static/'
url_prefix='/api/v1.0'

@api.route('/',methods=['GET'])
def index():
	return send_file(os.path.join('static','index.html'))

@api.route(url_prefix+'/signin',methods=['POST'])
def signin():
	data = request.json
	username = data.get("username")
	password = data.get("password")

	user = User.query.filter_by(email=username).first()
	if not user:
		return unauthorized('Unauthorized access!!')

	valid = user.verify_password(password)

	if not valid:
		return unauthorized('Unauthorized access!!') 

	return jsonify({'valid':True,'user':user.email,'token':user.generate_auth_token(\
		expiration=3600),'expiration':3600})

@api.route(url_prefix+'/register',methods=['GET','POST'])
def register():
	data = request.json
	username = data.get("username")
	password = data.get("password")
	
