#!/usr/bin/python3

"""
export YOURAPPLICATION_SETTINGS=/Users/nbmhqa571/Repositories/my-projects/bps-channel/building-rest-api-with-flask-2024/chapter-10/settings.cfg
gunicorn -w 4 main:app
gunicorn --config gunicorn_config.py main:app
export GUNICORN_WORKER_CLASS=gevent
export GUNICORN_WORKER_CLASS=tornado
"""

import jwt
import json
import traceback

from flask import Flask, jsonify, request, redirect, url_for, request_started, request_finished, got_request_exception, request_tearing_down, current_app
from flask.signals import Namespace
from marshmallow import Schema, fields, validate, ValidationError
from cryptography.fernet import Fernet
from pprint import pprint
from functools import wraps
from logging.config import dictConfig
from db.models import engine, get_user_by_credential, get_user_by_username, create_user, change_password, get_user_by_email_and_password
from db.forms import UserCreate, UserResetPassword, UserChangePassword
from sqlmodel import Session


# Example config from Flask
dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

app = Flask(__name__)

app.logger.info("Initializing the app ...")

app.config.from_envvar('YOURAPPLICATION_SETTINGS')


def log_request(sender, **extra):
    sender.logger.info('request_started_handler is invoked')


def log_response(sender, response, **extra):
	sender.logger.info('Request context is about to close down. Response: %s', json.dumps(response.json))


def log_exception(sender, exception, **extra):
    if not isinstance(exception, IndexError):
        return

    sender.logger.error(
        f"IndexError at {request.url!r}",
        exc_info=exception,
    )

def connection_cleanup(sender, **extra):
    sender.logger.info('Cleanup the connection ...')


request_started.connect(log_request, app)
request_finished.connect(log_response, app)
got_request_exception.connect(log_exception, app)
request_tearing_down.connect(connection_cleanup, app)

namespace = Namespace()
message_sent = namespace.signal('mail_sent')


@message_sent.connect
def message_sent_subscribe_1(app, recipient, body):
    app.logger.info("Executing message_sent_subscribe_1 from message_sent signal...")
    app.logger.info("Executing message_sent_subscribe_1. Recipient: %s" % (recipient))
    app.logger.info("Executing message_sent_subscribe_1. Body: %s" % (body))


@message_sent.connect
def message_sent_subscribe_2(app, recipient, body):
    app.logger.info("Executing message_sent_subscribe_2 from message_sent signal...")
    app.logger.info("Executing message_sent_subscribe_2. Recipient: %s" % (recipient))
    app.logger.info("Executing message_sent_subscribe_2. Body: %s" % (body))


@message_sent.connect
def message_sent_subscribe_3(app, recipient, body):
    app.logger.info("Executing message_sent_subscribe_3 from message_sent signal ...")
    app.logger.info("Executing message_sent_subscribe_3. Recipient: %s" % (recipient))
    app.logger.info("Executing message_sent_subscribe_3. Body: %s" % (body))


def encrypt_jwt_payload(key, payload):
	f = Fernet(bytes(key, "utf-8"))
	encrypted_value = f.encrypt(bytes(payload, "utf-8")).decode('utf-8')

	return encrypted_value


def decrypt_jwt_payload(key, payload):
	f = Fernet(bytes(key, "utf-8"))
	decrypted_value = f.decrypt(bytes(payload, "utf-8")).decode('utf-8')

	return decrypted_value


class ArticleSchema(Schema):
	title = fields.String(required=True, validate=validate.Length(min=1, max=128))
	content = fields.String()
	tags = fields.String()
	category_id = fields.Int(validate=validate.Range(min=1))
	user_id = fields.Int(validate=validate.Range(min=1))


def login_required(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):

		# begin decorator

		if "Authorization" in request.headers:
			bearer_token = request.headers["Authorization"]
			token = bearer_token.split(" ")[1]

			app.logger.error("Checking token!")

			if not bearer_token or not token:
				app.logger.error("Token is missing. Redirecting to login page!")
				
				response = {
					"message": "Missing auth token",
				}

				return jsonify(response), 401

			try:
				decoded_token = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
				decrypted_payload = json.loads(decrypt_jwt_payload(app.config["FERNET_KEY"], decoded_token["data"]))

				with Session(engine) as session:

					current_user = get_user_by_username(session, decrypted_payload['username'])

					if current_user is None:
						response = {
							"message": "Invalid Authentication token!",
						}

						return jsonify(response), 401

					if not current_user.is_active:
						response = {
							"message": "The user is not active. Please contact the administrator!"
						}
						return jsonify(response), 401

			except Exception as e:
				error_message = traceback.format_exc()

				response = {
				    "message": "Exception found when validating the token",
				    "error": error_message
				}

				return jsonify(response), 500

		else:
			app.logger.error("Auth header not found!")

			response = {
				"message": "Auth header not found!",
			}

			return jsonify(response), 400

		# end decorator

		return f(current_user, *args, **kwargs)

	return decorated_function


@app.route('/')
def get_home():

	response = {
		"message": "Welcome visitor",
		"debug": app.config["DEBUG"],
		"application_port": app.config["APP_PORT"],
		"remark": "We use Python config file",
	}

	return jsonify(response)


@app.route('/search')
@login_required
def get_search(current_user):
	q = request.args.get("q")
	qtype = request.args.get("qtype")
	page = request.args.get("page")
	limit = request.args.get("limit")

	if q is None:
		q = ""

	if qtype is None:
		qtype = "article"

	if page is None:
		page = 1

	if limit is None:
		limit = 10

	response = {
		"message": "Searching page!",
		"params": {
			"q": q,
			"qtype": qtype,
			"page": page,
			"limit": limit
		}
	}

	return jsonify(response)


@app.route('/article')
@login_required
def get_articles(current_user):
	response = {
		"message": "GET all articles ..."
	}

	return jsonify(response)


@app.route('/article', methods=["POST"])
@login_required
def create_article(current_user):
	try:
		payload = request.form
		ArticleSchema().load(payload)

		response = {
			"message": "POST new article ...",
			"payload": payload
		}

		status_code = 200

	except ValidationError as err:

		response = {
			"message": "Failed to create new article ...",
			"error": err.messages
		}

		status_code = 400

	return jsonify(response), status_code


@app.route('/article/<int:uid>')
@login_required
def get_article_by_id(current_user, uid):
	response = {
		"message": "GET article by ID ...",
		"id": uid
	}

	return jsonify(response)


@app.route('/article/<int:uid>', methods=["PUT"])
@login_required
def update_article_by_id(current_user, uid):
	try:
		payload = request.json
		ArticleSchema().load(payload)

		title = request.json["title"]
		content = request.json["content"]
		tags = request.json["tags"]
		category_id = request.json["category_id"]
		user_id = request.json["user_id"]

		response = {
			"message": "PUT edit article by ID ...",
			"id": uid,
			"payload": {
				"title": title,
				"content": content,
				"tags": tags,
				"category_id": category_id,
				"user_id": user_id,
			}
		}

		status_code = 200

	except ValidationError as err:
		app.logger.error(err.messages)

		response = {
			"message": "Failed to update existing article ...",
			"error": err.messages
		}

		status_code = 400

	return jsonify(response), status_code


@app.route('/article/<int:uid>', methods=["DELETE"])
@login_required
def delete_article_by_id(current_user, uid):
	response = {
		"message": "DELETE article by ID ...",
		"id": uid
	}

	message_sent.send(
        current_app._get_current_object(),
        recipient="johndoe@example.com",
        body="Your article is deleted by the owner ..."
    )

	return jsonify(response)


@app.route('/login', methods=["POST"])
def login():

	payload = request.json

	if not payload:
		response = {
			"message": "Username and password are missing",
		}

		return jsonify(response), 400

	with Session(engine) as session:
		user = get_user_by_credential(session, payload['username'], payload['password'])

		if user is None:
			response = {
				"message": "Login failed. Invalid credential",
			}

			return jsonify(response), 401
		else:
			token_payload = {
				"user_id": user.id,
				"username": user.username,
				"email": user.email,
			}

			jwt_payload = {
				"data": encrypt_jwt_payload(app.config["FERNET_KEY"], json.dumps(token_payload))
			}

			try:
				user = dict(user)
				del user['password']
				user["token"] = jwt.encode(
					payload=jwt_payload,
					key=app.config["SECRET_KEY"],
					algorithm="HS256"
				)

				return jsonify({
					"message":"Login success!",
					"data": user
				})
			except Exception as e:
				error_message = traceback.format_exc()

				return jsonify({
					"message":"Exception found when attempting to login",
					"error": error_message
				}), 500

			
@app.route('/signup', methods=["POST"])
def signup():

	payload = request.json

	if not payload:
		response = {
			"message": "Missing payload",
		}

		return jsonify(response), 400

	try:
		UserCreate.model_validate_json(json.dumps(request.json))
	except Exception as e:
		return jsonify({
				"message":"Exception found when attempting to validate signup payload",
				"error": e.errors()
			}), 500

	if payload['password'] != payload['confirm_password']:
		response = {
			"message": "Password and confirm_password are not match",
		}

		return jsonify(response), 400

	try:
		with Session(engine) as session:
			temp_user = create_user(session, payload['username'], payload['email'], payload['password'])
			if temp_user is not None:
				del payload['password']
				del payload['confirm_password']

				return jsonify({
						"message":"Signup success!",
						"data": payload
					})
			else:
				response = {
					"message": "Signup failed. User is already exists!",
				}

				return jsonify(response), 400
	except Exception as e:
		error_message = traceback.format_exc()

		return jsonify({
			"message":"Exception found when attempting to signup",
			"error": error_message
		}), 500


@app.route('/reset-password', methods=["POST"])
def reset_password():
	# id fetched from payload on the link within the e-mail

	payload = request.json

	if not payload:
		response = {
			"message": "Missing payload",
		}

		return jsonify(response), 400

	try:
		UserResetPassword.model_validate_json(json.dumps(request.json))
	except Exception as e:
		return jsonify({
				"message":"Exception found when attempting to validate reset password payload",
				"error": e.errors()
			}), 500

	if payload['password'] != payload['confirm_password']:
		response = {
			"message": "Password and confirm_password are not match",
		}

		return jsonify(response), 400

	try:
		with Session(engine) as session:
			temp_user = change_password(session, payload['id'], payload['email'], payload['password'])

			if temp_user is not None:
				del payload['password']
				del payload['confirm_password']

				return jsonify({
						"message":"Reset password success!",
						"data": payload
					})
			else:
				response = {
					"message": "Reset password failed. User is not exists!",
				}

				return jsonify(response), 400
	except Exception as e:
		error_message = traceback.format_exc()

		return jsonify({
			"message":"Exception found when attempting to reset password",
			"error": error_message
		}), 404


@app.route('/change-password', methods=["POST"])
@login_required
def change_user_password(current_user):
	# this function shouldn't have similar name with function from models
	# id fetched from payload on the JWT

	payload = request.json

	if not payload:
		response = {
			"message": "Missing payload",
		}

		return jsonify(response), 400

	try:
		UserChangePassword.model_validate_json(json.dumps(request.json))
	except Exception as e:
		return jsonify({
				"message":"Exception found when attempting to validate change password payload",
				"error": e.errors()
			}), 500

	# a. check if new password is actually same with current_password
	if payload['current_password'] == payload['new_password']:
		response = {
			"message": "Please don't use current_password for your new password",
		}

		return jsonify(response), 400

	# b. check if new password and confirm new password are actually same
	if payload['new_password'] != payload['confirm_new_password']:
		response = {
			"message": "new password and confirm new password are not match",
		}

		return jsonify(response), 400

	try:
		with Session(engine) as session:
			# c. check if user is exist by using current_password
			existing_user = get_user_by_email_and_password(session, payload['email'], payload['current_password'])

			temp_user = change_password(session, existing_user.id, existing_user.email, payload['new_password'])

			if temp_user is not None:
				del payload['current_password']
				del payload['new_password']
				del payload['confirm_new_password']

				return jsonify({
						"message":"Change password success!",
						"data": payload
					})
			else:
				response = {
					"message": "Change password failed. User is not exists!",
				}

				return jsonify(response), 400
	except Exception as e:
		error_message = traceback.format_exc()

		return jsonify({
			"message":"Exception found when attempting to change password",
			"error": error_message
		}), 404


if __name__ == '__main__':
	app.logger.info("Application is running now")
	app.run(debug=app.config['DEBUG'], port=app.config['APP_PORT'])
