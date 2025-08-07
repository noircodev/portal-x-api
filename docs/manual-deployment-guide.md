# **Django Project Deployment Guide**

**Project Name:** Portal X Event  
**Version:** 1.0

---

## **Table of Contents**

1. [**Prerequisites**](#1-prerequisites)
2. [**System Dependencies Installation**](#2-system-dependencies-installation)
3. [**Database Setup (PostgreSQL + PostGIS)**](#3-database-setup-postgresql--postgis)
4. [**Virtual Environment Setup**](#4-virtual-environment-setup)
5. [**Gunicorn Configuration**](#5-gunicorn-configuration)
6. [**Nginx Reverse Proxy Setup**](#6-nginx-reverse-proxy-setup)
7. [**SSL Certificate with Let’s Encrypt**](#7-ssl-certificate-with-lets-encrypt)
8. [**Meilisearch Setup (Search Engine)**](#8-meilisearch-setup-search-engine)
9. [**Cron Jobs & Management Commands**](#9-cron-jobs--management-commands)
10. [**Final Steps & Restarting Services**](#10-final-steps--restarting-services)

---

## **1. Prerequisites**

Before proceeding, ensure you have:

- [ ] A Linux-based server (Ubuntu/Debian recommended)
- [ ] `sudo` access
- [ ] Domain name pointed to the server (e.g., `staging.portalx.space`)
- [ ] Docker installed (for Meilisearch)

---

## **2. System Dependencies Installation**

Run the following commands to install required packages:

```sh
sudo apt update
sudo apt install -y python3-pip python3-virtualenv python3-certbot-nginx \
python3-dev libpq-dev postgresql postgresql-contrib postgis nginx postfix mailutils
```

### **Explanation:**

- `python3-pip`, `python3-virtualenv`: For Python environment management
- `libpq-dev`, `postgresql`: For PostgreSQL database
- `postgis`: For geospatial database support
- `nginx`: Web server for reverse proxy
- `postfix`, `mailutils`: For email functionality

---

## **3. Database Setup (PostgreSQL + PostGIS)**

### **Step 1: Log in to PostgreSQL**

```sh
sudo -u postgres psql
```

### **Step 2: Execute SQL Commands**

Run the following inside `psql`:

```sql
-- Create database and user
CREATE DATABASE portal_x_event;
CREATE USER web WITH PASSWORD 'your_strong_password';

-- Configure user permissions
ALTER ROLE web SUPERUSER;
ALTER ROLE web SET client_encoding TO 'utf8';
ALTER ROLE web SET default_transaction_isolation TO 'read committed';
ALTER ROLE web SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE portal_x_event TO web;

-- Enable PostGIS extension
\c portal_x_event;
CREATE EXTENSION IF NOT EXISTS postgis;

-- Add full-text search vector (if needed)
ALTER TABLE event_event ADD COLUMN search_vector tsvector;
CREATE INDEX event_search_vector_idx ON event_event USING GIN(search_vector);
```

### **Step 3: Exit PostgreSQL**

```sql
\q
```

---

## **4. Virtual Environment Setup**

Create and activate a Python virtual environment:

```sh
mkdir app
cd app
virtualenv .venv/
source .venv/bin/activate  # Activate the virtual environment
```

Install project dependencies (assuming `requirements.txt` exists):

```sh
pip install -r requirements/main.txt
```

---

## **5. Gunicorn Configuration**

### **Step 1: Create Gunicorn Socket File**

```sh
sudo nano /etc/systemd/system/gunicorn.socket
```

Paste:

```ini
[Unit]
Description=Gunicorn socket file

[Socket]
ListenStream=/run/gunicorn.sock
SocketUser=web
SocketGroup=www-data
SocketMode=660
Backlog=512
RemoveOnStop=true

[Install]
WantedBy=sockets.target
```

### **Step 2: Create Gunicorn Service File**

```sh
sudo nano /etc/systemd/system/gunicorn.service
```

Paste:

```ini
[Unit]
Description=Gunicorn Daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=web
Group=www-data
WorkingDirectory=/home/web/app

ExecStart=/home/web/app/.venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --threads 2 \
          --timeout 300 \
          --keep-alive 5 \
          --limit-request-line 8190 \
          --limit-request-field_size 8190 \
          --preload \
          --bind unix:/run/gunicorn.sock \
          core.wsgi:application

ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### **Step 3: Start & Enable Gunicorn**

```sh
sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.socket
```

---

## **6. Nginx Reverse Proxy Setup**

### **Step 1: Create Nginx Config**

```sh
sudo nano /etc/nginx/sites-available/staging.portalx.space
```

Paste:

```nginx
server {
    listen 80;
    server_name staging.portalx.space;
    client_max_body_size 20M;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /home/web/app;
    }
    location /media/ {
        root /home/web/app;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
}
```

### **Step 2: Enable the Site**

```sh
sudo ln -s /etc/nginx/sites-available/staging.portalx.space /etc/nginx/sites-enabled
```

### **Step 3: Add User to `www-data` Group**

```sh
sudo usermod -a -G web www-data
```

---

## **7. SSL Certificate with Let’s Encrypt**

### **Step 1: Install Certbot**

```sh
sudo apt install certbot python3-certbot-nginx -y
```

### **Step 2: Obtain SSL Certificate**

```sh
sudo certbot --nginx -d staging.portalx.space
```

---

## **8. Meilisearch Setup (Search Engine)**

### **Step 1: Create Environment File**

```sh
sudo mkdir -p /opt/meilisearch/
sudo nano /opt/meilisearch/.env
```

Paste:

```sh
MEILI_MASTER_KEY=your_strong_master_key
MEILI_ENV=production
MEILI_HTTP_ADDR=0.0.0.0:7700
```

### **Step 2: Run Meilisearch in Docker**

```sh
docker run -d \
  --name meilisearch \
  -p 7700:7700 \
  --env-file /opt/meilisearch/.env \
  -v /opt/meilisearch/data.ms:/meili_data \
  --restart=always \
  getmeili/meilisearch:v1.14
```

---

## **9. Cron Jobs & Management Commands**

### **Step 1: Run Initial Setup Commands**

```sh
./manage.py makemigrations
./manage.py migrate
./manage.py collectstatic --noinput
./manage.py create_states
./manage.py create_cities

```

### **Step 2: Setup Cron Jobs**

```sh
./scripts/setup_cron_job.sh
```

---

## **10. Final Steps & Restarting Services**

### **Restart Services**

```sh
sudo systemctl restart gunicorn nginx
```

### **Verify Services**

```sh
sudo systemctl status gunicorn nginx
```

### **Access the Site**

Visit:

```
https://staging.portalx.space
```

---

## **Allow Passwordless `sudo` for Restarting Gunicorn**

Create or edit a sudoers rule for your deployment user (e.g. `web`):

```bash
sudo visudo
```

Add this line at the end:

```bash
web ALL=(ALL) NOPASSWD: /bin/systemctl restart gunicorn, /bin/systemctl status gunicorn*

```

> This grants passwordless `sudo` access for only the `restart` and `status` command for `gunicorn`, not full root access.

---

## **Final Notes**

- **Domain Configuration**: Make sure `staging.portalx.space` points to the correct server IP.

- **Firewall:** Open necessary ports (80, 443, 7700).

### **Logs:**

- **Gunicorn:** journalctl -u gunicorn

- **NGINX:** /var/log/nginx/error.log

- **Security:** Change all default passwords and master keys before deployment.

---

## **Troubleshooting**

- **Gunicorn Errors:** Check logs with `journalctl -u gunicorn`
- **Nginx Errors:** Check logs with `sudo tail -f /var/log/nginx/error.log`
- **PostgreSQL Issues:** Ensure user `web` has correct permissions

---

**Deployment Complete!** Your Django project is now live.
