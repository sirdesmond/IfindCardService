from flask import g,jsonify,request
from . import api
from ..models import User 
from flask.ext.httpauth import HTTPBasicAuth
from ..errors import unauthorized,forbidden

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(email_or_token,password):
	if email_or_token == '':
		#TODO: set up Anonymous User#
		g.current_user is None
		return True
	if password == '':
		g.current_user =User.verify_auth_token(email_or_token)
		g.token_used = True
		return g.current_user is not None
	user = User.query.filter_by(email=email_or_token).first()
	if not user:
		return False
	g.current_user = user
	g.token_used = False
	return user.verify_password(password)

@auth.error_handler
def auth_error():
	return unauthorized('Invalid credentials')


@api.before_request
def before_request():
	pass
	#if not g.current_user.confirmed:
	#	return forbidden('Unconfirmed account')

@api.route('/token')
@auth.login_required
def get_token():
	return jsonify({'token': g.current_user.generate_auth_token(\
		expiration=3600),'expiration':3600})		

