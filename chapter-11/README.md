# README


Keypoints:

- ASGI will become superset for WSGI
- ASGI support long-poll HTTP and Websocket protocol which WSGI doesn't support
- ASGI is compatible with WSGI application by using the translation wrapper such as `asgiref`
- ASGI-compatible HTTP Server for Python: Uvicorn, Daphne, Hypercorn, Granian
- Uvicorn, asgiref and Gunicorn could be used to serve WSGI-compatible web framework such as Flask, Django, Falcon, etc.

References:

- https://docs.gunicorn.org/en/stable/settings.html#worker-class
- https://flask.palletsprojects.com/en/3.0.x/deploying/gunicorn/
- https://peps.python.org/pep-3333/
- http://www.gevent.org/
- https://www.tornadoweb.org/en/stable/guide/intro.html
- https://dev.to/lsena/gunicorn-worker-types-how-to-choose-the-right-one-4n2c
- https://flask.palletsprojects.com/en/2.3.x/deploying/asgi/
- https://asgi.readthedocs.io/en/latest/specs/main.html
- https://asgi.readthedocs.io/en/latest/introduction.html
- https://www.uvicorn.org/#running-with-gunicorn