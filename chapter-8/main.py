#!/usr/bin/python3

"""
export YOURAPPLICATION_SETTINGS=/Users/nbmhqa571/Repositories/my-projects/bps-channel/building-rest-api-with-flask-2024/chapter-8/settings.cfg
"""

import jwt
import json
import traceback

from flask import Flask, jsonify, request, redirect, url_for
from marshmallow import Schema, fields, validate, ValidationError
from cryptography.fernet import Fernet
from functools import wraps
from logging.config import dictConfig


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
			token_len = len(bearer_token.split(" "))

			app.logger.info("Checking token!")

			if not bearer_token or (token_len < 2):
				app.logger.error("Token is missing. Please login first!")
				
				response = {
					"message": "Missing auth token",
				}

				return jsonify(response), 401

			token = bearer_token.split(" ")[1]

			try:
				decoded_token = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
				
				decrypted_payload = decrypt_jwt_payload(app.config["FERNET_KEY"], decoded_token["data"])

				current_user = {
					"id" : 1,
					"username": "johndoe",
					"active": True
				}

				if current_user is None:
					response = {
						"message": "Invalid Authentication token!",
					}

					return jsonify(response), 401

				if not current_user["active"]:
					abort(403)

			except Exception as e:
				app.logger.error("Exception found when validating the token")

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
		app.logger.error("Exception found when validating the request body")

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
		app.logger.critical("Exception found when validating the request body when updating article")

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

	return jsonify(response)


@app.route('/login', methods=["POST"])
def login():

	payload = request.json

	if not payload:
		response = {
			"message": "Username and password are missing",
		}

		return jsonify(response), 400

	is_validated = True

	if is_validated is False:
		response = {
			"message": "Login failed. Invalid credential",
		}

		return jsonify(response), 400

	user = {
    	"id" : 1,
    	"username": "johndoe",
    	"active": True
    }

	if user:
		token_payload = {
			"user_id": user["id"],
			"username": user["username"]
		}

		jwt_payload = {
			"data": encrypt_jwt_payload(app.config["FERNET_KEY"], json.dumps(token_payload))
		}

		try:
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
			app.logger.error("Exception found when generating jwt")

			error_message = traceback.format_exc()

			return jsonify({
				"message":"Exception found when attempting to login",
				"error": error_message
			}), 500
	else:
		response = {
			"message": "Login failed. User not found",
		}

		return jsonify(response), 401

if __name__ == '__main__':
	app.logger.info("Application is running now")
	app.run(debug=app.config['DEBUG'], port=app.config['APP_PORT'])
