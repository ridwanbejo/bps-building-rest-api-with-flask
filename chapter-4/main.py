#!/usr/bin/python3

"""
export YOURAPPLICATION_SETTINGS=/Users/nbmhqa571/Repositories/my-projects/bps-channel/building-rest-api-with-flask-2024/chapter-4/settings.cfg
"""

from flask import Flask, jsonify, request, redirect, url_for


app = Flask(__name__)

app.config.from_envvar('YOURAPPLICATION_SETTINGS')


@app.route('/')
def get_home():
	response = {
		"message": "Welcome visitor",
		"app_port": app.config['APP_PORT'],
		"debug": app.config['DEBUG'],
		"remark": "We use Python config file"
	}

	return jsonify(response)


@app.route('/search')
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
def get_articles():
	response = {
		"message": "GET all articles ..."
	}

	return jsonify(response)


@app.route('/article', methods=["POST"])
def create_article():
	payload = request.form
	response = {
		"message": "POST new article ...",
		"payload": payload
	}

	return jsonify(response)


@app.route('/article/<int:uid>')
def get_article_by_id(uid):
	response = {
		"message": "GET article by ID ...",
		"id": uid
	}

	return jsonify(response)


@app.route('/article/<int:uid>', methods=["PUT"])
def update_article_by_id(uid):
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

	return jsonify(response)


@app.route('/article/<int:uid>', methods=["DELETE"])
def delete_article_by_id(uid):
	response = {
		"message": "DELETE article by ID ...",
		"id": uid
	}

	return jsonify(response)


@app.route('/redirect')
def get_redirect():
	return redirect(url_for('get_landing'))


@app.route('/landing')
def get_landing():
	response = {
		"message": "Landing from redirection..."
	}

	return jsonify(response)


if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'], port=app.config['APP_PORT'])
