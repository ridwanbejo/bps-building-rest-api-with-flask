#!/usr/bin/python3


"""
export FLASK_SECRET_KEY="5f352379324c22463451387a0aec5d2f"
export FLASK_APP_PORT=8080
export FLASK_DEBUG=True
"""

from flask import Flask, jsonify, request


app = Flask(__name__)
app.config.from_prefixed_env()


@app.route('/')
def get_home():
	response = {
		"message": "Welcome visitor",
		"app_port": app.config['APP_PORT'],
		"debug": app.config['DEBUG'],
		"remark": "We use prefixed environment variables"
	}

	return jsonify(response)

@app.route('/hello')
def get_hello():
	response = {
		"message": "Hello world!"
	}

	return jsonify(response)


if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'], port=app.config['APP_PORT'])