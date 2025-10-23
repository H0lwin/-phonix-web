# 🚀 Phonix Production Quick Start

## 5 مرحله برای آماده‌سازی Production

### مرحله 1: تنظیم محیط (10 دقیقه)

```bash
# 1. Virtual Environment
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# 2. Dependencies نصب کنید
pip install -r requirements.txt
pip install gunicorn

# 3. .env فایل ایجاد کنید
cp .env.example .env

# .env را با Editor باز کنید و این موارد را تغییر دهید:
# - DEBUG=False
# - SECRET_KEY (با دستور زیر تولید کنید)
# - ALLOWED_HOSTS
# - DATABASE_*
```

**SECRET_KEY تولید کنید:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

### مرحله 2: دیتابیس (5 دقیقه)

```bash
# MySQL دیتابیس ایجاد کنید:
# (از MySQL command line یا PhpMyAdmin)

# CREATE USER 'phonix_user'@'localhost' IDENTIFIED BY 'your_strong_password';
# CREATE DATABASE Phonix_suite CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
# GRANT ALL PRIVILEGES ON Phonix_suite.* TO 'phonix_user'@'localhost';
# FLUSH PRIVILEGES;

# سپس migrations اعمال کنید:
python manage.py migrate
```

---

### مرحله 3: Static Files (3 دقیقه)

```bash
# Static files جمع‌آوری کنید
python manage.py collectstatic --noinput

# مالک تغییر دهید (اگر روی Linux است)
# sudo chown -R www-data:www-data /path/to/phonix-dj
```

---

### مرحله 4: ادمین ایجاد کنید (5 دقیقه)

**روش تعاملی (توصیه شده):**
```bash
python init_admin.py
```

سپس یکی از گزینه‌ها را انتخاب کنید:
- `1` برای ایجاد ادمین جدید
- `2` برای بروزرسانی ادمین موجود

---

### مرحله 5: تست و Deploy (5 دقیقه)

```bash
# تست‌های امنیتی Django
python manage.py check --deploy

# Gunicorn شروع کنید (تست)
gunicorn --workers=4 --bind=127.0.0.1:8000 phonix.wsgi:application

# یا برای Systemd service:
sudo systemctl start phonix
```

---

## ✅ Pre-Flight Checklist

قبل از go-live این موارد را بررسی کنید:

```
[ ] DEBUG = False
[ ] SECRET_KEY منحصر به‌فرض و قوی است
[ ] DATABASE_PASSWORD قوی است
[ ] ALLOWED_HOSTS تنها دامنه‌های واقعی شامل است
[ ] SSL Certificate نصب شد
[ ] Static Files collectstatic شدند
[ ] ادمین ایجاد شد
[ ] Database migrations اعمال شدند
[ ] Gunicorn/uWSGI Systemd service تنظیم شده
[ ] Nginx/Apache reverse proxy تنظیم شده
[ ] Backups روزانه تنظیم شدند
[ ] Monitoring و Logging فعال است
[ ] Database backups آماده است
```

---

## 🔒 Security Reminders

1. **Never commit `.env` file to git!**
   ```bash
   # .gitignore میں این موجود است:
   .env
   ```

2. **Strong Passwords:**
   - Database: 16+ characters مع special characters
   - Admin: 8+ characters مع uppercase, lowercase, numbers

3. **HTTPS Only:**
   - Let's Encrypt استفاده کنید (رایگان)
   - Nginx میں HTTP به HTTPS redirect کنید

4. **Regular Backups:**
   ```bash
   # روزانه بکاپ
   0 2 * * * mysqldump -u user -p'pass' Phonix_suite > /backups/phonix_$(date +%Y%m%d).sql
   ```

---

## 🐛 Troubleshooting

### Static Files Not Loading?
```bash
# دوباره جمع‌آوری کنید
python manage.py collectstatic --clear --noinput

# Nginx میں alias صحیح باشد
# location /static/ { alias /path/to/staticfiles/; }
```

### Database Connection Error?
```bash
# .env میں DATABASE_* متغیرها چک کنید
python manage.py dbshell  # تست اتصال

# MySQL Server چل رہی ہے؟
sudo systemctl status mysql
```

### Permission Denied?
```bash
# Nginx/Apache user کو media و staticfiles رسائی دیں
sudo chown -R www-data:www-data /path/to/phonix-dj
sudo chmod -R 755 /path/to/phonix-dj
```

---

## 📚 نمونه Configuration Files

### Nginx Config (production)

```nginx
upstream phonix {
    server 127.0.0.1:8000;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    location /static/ {
        alias /path/to/phonix-dj/staticfiles/;
        expires 30d;
    }
    
    location / {
        proxy_pass http://phonix;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
    }
}

server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

### Gunicorn Systemd Service

```ini
# /etc/systemd/system/phonix.service
[Unit]
Description=Phonix Django Application
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/path/to/phonix-dj
ExecStart=/path/to/phonix-dj/venv/bin/gunicorn \
    --workers=4 \
    --bind=127.0.0.1:8000 \
    --timeout=30 \
    phonix.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

سپس:
```bash
sudo systemctl daemon-reload
sudo systemctl enable phonix
sudo systemctl start phonix
```

---

## 📞 اگر کمک نیاز است

- `PRODUCTION_DEPLOYMENT.md` را بخوانید (تفصیلی)
- `phonix/settings.py` میں تنظیمات امنیتی بررسی کنید
- Django documentation: https://docs.djangoproject.com/

**Happy Deploying! 🎉**