/usr/bin/python /usr/local/bin/gunicorn -c gunicorn.conf web:app -D -t 6000 --pid app.pid --error-logfile error.log --log-level info  --log-file=app.log --access-logfile access.log
