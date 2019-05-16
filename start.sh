cd $3
source env/bin/activate
FLASK_DEBUG=1 MICROBLOGPUB_DEBUG=1 FLASK_APP=app.py POUSSETACHES_AUTH_KEY=$1 flask run -p $2 --with-threads
