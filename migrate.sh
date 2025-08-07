source .venv/bin/activate
./manage.py makemigrations
./manage.py migrate
./manage.py collectstatic
sudo systemctl restart gunicorn
