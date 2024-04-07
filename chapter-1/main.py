#!/usr/bin/python3

from flask import Flask, jsonify, request


app = Flask(__name__)

@app.route('/')
def get_home():
	response = {
		"message": "Welcome visitor"
	}

	return jsonify(response)

@app.route('/hello')
def get_hello():
	response = {
		"message": "Hello world!!!!!!!!"
	}

	return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True, port=8080)
