.SILENT: install pt-install services config password
PYTHON=python

install:
	echo "Setting up Python Virtualenv..."
	virtualenv env
	$$(source env/bin/activate)
	echo "Installing dependencies..."
	pip install -r requirements.txt
	echo "done"

pt-install:
	printf "Installing poussetaches..."
	cp -R poussetaches /usr/bin/poussetaches
	echo "done"

services:
	./mkservices.sh

config:
	./mkconfig.sh

password:
	$(PYTHON) -c "import bcrypt; from getpass import getpass; print(bcrypt.hashpw(getpass().encode('utf-8'), bcrypt.gensalt()).decode('utf-8'))"
	echo "Please copy this code into the 'pass' variable in config/me.yml"
