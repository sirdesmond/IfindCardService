from sqlalchemy import or_
from flask import jsonify,request,make_response,send_file,url_for
from flask.ext.login import login_user, logout_user, login_required, \
	current_user
from ..email import send_email
from . import auth
from .. import db
from ..models import User
from ..decorators import crossdomain
from ..errors import unauthorized,forbidden
import os


static_folder = '/app/static/'

# @auth.before_app_request
# def before_request():
#     if current_user.is_authenticated():
#         current_user.ping()
#         if not current_user.confirmed \
#                 and request.endpoint[:5] != 'auth.':
#             return redirect(url_for('auth.unconfirmed'))



@auth.route('/signin',methods=['GET','POST','OPTIONS'])
@crossdomain(origin="*",headers="Content-Type")
def signin():
   
    data = request.json
    if 'password' in data:
        password =  data['password']
    if 'username' in data:
        username = data['username']
        user = User.query.filter_by(username=username).first()
    if 'email' in data:
        email =  data['email']
        user = User.query.filter_by(email=email).first()


    if not user:
    	response = make_response(unauthorized('Unauthorized access!!'))
        return response
    valid = user.verify_password(password)

    if not valid:
    	response =  make_response(unauthorized('Unauthorized access!!')) 
        return response

    response =  make_response(jsonify({'valid':True,'user':user.email,'token':user.generate_auth_token(\
    	expiration=3600),'expiration':3600}))
    return response     


@auth.route('/signout')
@login_required
def signout():
    logout_user()
    ####flash message here

    #send file to signin page
    return redirect(url_for('.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
	email = request.form['email']
	username = request.form['username']
	password = request.form['password']

	user = User(email=email,username=username,password=password)
	db.session.add(user)
	db.session.commit()
	token = user.generate_confirmation_token()
	send_email(user.email, 'Confirm Your Account',
	            user=user, token=token)

	return jsonify({'email':email,'token':token})


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
    	pass
       # flash('You have confirmed your account. Thanks!')
    else:
    	pass
        #flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('.index'))


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
               'auth/email/confirm', user=current_user, token=token)
    #flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('.index'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous() or current_user.confirmed:
        return redirect(url_for('.index'))
    return send_file('auth/unconfirmed.html')



@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            flash('Your password has been updated.')
            return redirect(url_for('.index'))
        else:
            pass
    return render_template("auth/change_password.html", form=form)


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous():
        return redirect(url_for('main.index'))
    
    data = request.json
    email = data["email"]
    user = User.query.filter_by(email=email).first()
    if user:
        token = user.generate_reset_token()
        send_email(user.email, 'Reset Your Password',
                   'auth/email/reset_password',
                   user=user, token=token,
                   next=request.args.get('next'))
        
    return redirect(url_for('auth.signin'))

@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous():
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('main.index'))
        if user.reset_password(token, form.password.data):
            flash('Your password has been updated.')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, 'Confirm your email address',
                       'auth/email/change_email',
                       user=current_user, token=token)
            flash('An email with instructions to confirm your new email '
                  'address has been sent to you.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password.')
    return render_template("auth/change_email.html", form=form)


@auth.route('/change-email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash('Your email address has been updated.')
    else:
        flash('Invalid request.')
    return redirect(url_for('main.index'))