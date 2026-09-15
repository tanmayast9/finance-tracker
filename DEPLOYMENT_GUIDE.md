# Flask Finance App - Production Deployment Guide

## Step 1: Update Dependencies

```bash
pip install -r requirements.txt
```

This includes:
- `gunicorn` - Production WSGI server
- `python-dotenv` - Environment variable management

## Step 2: Test Gunicorn Locally

```bash
gunicorn -c gunicorn_config.py run:app
```

Visit `http://localhost:5000` to verify it works.

---

## Step 3: Deploy on Linux/VPS (Ubuntu/Debian)

### A. Copy Files to Server

```bash
scp -r /path/to/finance user@your-server.com:/home/user/flask-app
ssh user@your-server.com
```

### B. Install System Dependencies

```bash
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv supervisor nginx
```

### C. Create Virtual Environment

```bash
cd /home/user/flask-app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### D. Set Up Environment Variables

Create `.env` file:

```bash
cat > /home/user/flask-app/.env << EOF
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
DATABASE_URL=mysql+pymysql://username:password@localhost/finance_db
EOF
```

**IMPORTANT:** Never commit `.env` to Git!

### E. Create Supervisor Configuration

```bash
# Copy the config file
sudo cp /home/user/flask-app/flask-finance.conf /etc/supervisor/conf.d/

# Edit it for your paths
sudo nano /etc/supervisor/conf.d/flask-finance.conf
```

**Update these paths:**
- `directory=/home/user/flask-app`
- `command=/home/user/flask-app/venv/bin/gunicorn -c gunicorn_config.py run:app`

**Update database URL:**
```ini
environment=FLASK_ENV=production,DATABASE_URL=mysql+pymysql://user:pass@localhost/finance_db
```

### F. Start Supervisor

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start flask-finance
sudo supervisorctl status  # Check if running
```

### G. Set Up Nginx

```bash
# Copy the config
sudo cp /home/user/flask-app/nginx-config.conf /etc/nginx/sites-available/flask-app

# Edit for your domain
sudo nano /etc/nginx/sites-available/flask-app
```

**Update:**
- `server_name yourdomain.com;` → your actual domain
- `/path/to/finance` → `/home/user/flask-app`

```bash
# Enable the site
sudo ln -s /etc/nginx/sites-available/flask-app /etc/nginx/sites-enabled/

# Test config
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

### H. Set Up SSL (Let's Encrypt)

```bash
sudo apt-get install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot certonly --nginx -d yourdomain.com

# Uncomment SSL section in nginx-config.conf and reload
sudo systemctl reload nginx
```

---

## Step 4: Verify Everything is Running

```bash
# Check Supervisor status
sudo supervisorctl status flask-finance

# Check Gunicorn process
ps aux | grep gunicorn

# Check Nginx
sudo systemctl status nginx

# Test health endpoint
curl http://yourdomain.com/health

# Check logs
tail -f /var/log/flask-finance.log
tail -f /var/log/flask-finance-error.log
```

---

## Step 5: Auto-Restart on Server Reboot

```bash
# Enable supervisor to auto-start
sudo systemctl enable supervisor

# Verify
sudo systemctl status supervisor
```

---

## Monitoring & Maintenance

### Restart Flask App
```bash
sudo supervisorctl restart flask-finance
```

### View Logs
```bash
# Recent logs
tail -n 50 /var/log/flask-finance.log

# Real-time logs
tail -f /var/log/flask-finance.log

# Error logs
tail -f /var/log/flask-finance-error.log
```

### Update Code
```bash
cd /home/user/flask-app
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo supervisorctl restart flask-finance
```

### Check Resource Usage
```bash
# Memory & CPU usage
top

# Disk space
df -h

# Process info
ps aux | grep gunicorn
```

---

## Health Check

Add to your Flask app (already in app.py):

```python
@app.route('/health')
def health():
    return {'status': 'ok'}, 200
```

Test it:
```bash
curl http://yourdomain.com/health
```

---

## Troubleshooting

### App not starting
```bash
sudo supervisorctl tail -f flask-finance stderr
```

### 502 Bad Gateway
- Check if Gunicorn is running: `sudo supervisorctl status`
- Check Nginx logs: `sudo tail -f /var/log/nginx/error.log`
- Verify port 5000 is bound: `sudo netstat -tuln | grep 5000`

### Database connection issues
- Verify MySQL is running: `sudo systemctl status mysql`
- Check `.env` DATABASE_URL is correct
- Test connection: `mysql -u username -p -h localhost`

### Permission issues
```bash
# Set permissions
sudo chown -R www-data:www-data /home/user/flask-app
sudo chmod -R 755 /home/user/flask-app
```

---

## Next Steps

1. ✅ Deploy on your Linux/VPS server
2. ✅ Point your domain DNS to server IP
3. ✅ Set up SSL certificate
4. ✅ Monitor logs regularly
5. ✅ Set up backups for database

Your Flask app will now run **24/7** automatically!
