source .venv/bin/activate
gunicorn -w 1 -k eventlet run:app -b 127.0.0.1:8002 --log-level debug --daemon