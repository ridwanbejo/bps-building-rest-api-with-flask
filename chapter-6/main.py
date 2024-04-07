#!/usr/bin/python3

"""
export YOURAPPLICATION_SETTINGS=/Users/nbmhqa571/Repositories/my-projects/bps-channel/building-rest-api-with-flask-2024/chapter-6/settings.cfg
"""

from flask import Flask, jsonify, request, redirect, url_for
from marshmallow import Schema, fields, validate, ValidationError
from pprint import pprint
from functools import wraps


app = Flask(__name__)

app.config.from_envvar('YOURAPPLICATION_SETTINGS')


class ArticleSchema(Schema):
	title = fields.String(required=True, validate=validate.Length(min=1, max=128))
	content = fields.String()
	tags = fields.String()
	category_id = fields.Int(validate=validate.Range(min=1))
	user_id = fields.Int(validate=validate.Range(min=1))


def login_required(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		pprint(request.headers)

		# begin decorator

		if "Authorization" in request.headers:
			token = request.headers["Authorization"]
			print("Checking token!")

			if not token:
				print("Token invalid. Redirecting to login page!")
				return redirect(url_for('login', next=request.url))
		else:
			print("Auth header not found. Redirecting to login page!")
			return redirect(url_for('login', next=request.url))

		# end decorator

		return f(*args, **kwargs)
	return decorated_function


@app.route('/')
@login_required
def get_home():
	response = {
		"message": "Welcome visitor",
		"app_port": app.config['APP_PORT'],
		"debug": app.config['DEBUG'],
		"remark": "We use Python config file"
	}

	return jsonify(response)


@app.route('/search')
@login_required
def get_search():
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
def get_articles():
	response = {
		"message": "GET all articles ..."
	}

	return jsonify(response)


@app.route('/article', methods=["POST"])
@login_required
def create_article():
	try:
		payload = request.form
		ArticleSchema().load(payload)

		response = {
			"message": "POST new article ...",
			"payload": payload
		}

		status_code = 200

	except ValidationError as err:
		pprint(err.messages)

		response = {
			"message": "Failed to create new article ...",
			"error": err.messages
		}

		status_code = 400

	return jsonify(response), status_code


@app.route('/article/<int:uid>')
@login_required
def get_article_by_id(uid):
	response = {
		"message": "GET article by ID ...",
		"id": uid
	}

	return jsonify(response)


@app.route('/article/<int:uid>', methods=["PUT"])
@login_required
def update_article_by_id(uid):
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
		pprint(err.messages)

		response = {
			"message": "Failed to update existing article ...",
			"error": err.messages
		}

		status_code = 400

	return jsonify(response), status_code


@app.route('/article/<int:uid>', methods=["DELETE"])
@login_required
def delete_article_by_id(uid):
	response = {
		"message": "DELETE article by ID ...",
		"id": uid
	}

	return jsonify(response)


@app.route('/login')
def login():
	return jsonify({"message":"Require login. Please specify your credential!"})

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'], port=app.config['APP_PORT'])