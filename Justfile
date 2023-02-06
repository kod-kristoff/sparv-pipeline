venv:
	test -d venv || python -m venv venv
	venv/bin/pip install wheel

dev:
	venv/bin/pip install -r requirements.txt

