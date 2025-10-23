# تنظیم Session Timeout - 30 دقیقه

## خلاصه تغییرات 🔄

### 1️⃣ **صفحه `index.html` حذف شد**
   - صفحه اولیه اب Django میشود، نه یک صفحه static
   - کاربر هنگام ورود به `/` خودکار به صفحه لاگین یا داشبورد ریدایرکت می‌شود

### 2️⃣ **تنظیمات Session در `settings.py`**
```python
SESSION_COOKIE_AGE = 1800              # 30 دقیقه = 1800 ثانیه
SESSION_SAVE_EVERY_REQUEST = False     # Timeout absolute است
```

**توضیح:**
- `SESSION_COOKIE_AGE = 1800`: کاربر هر 30 دقیقه باید دوباره لاگین کند
- `SESSION_SAVE_EVERY_REQUEST = False`: این timeout absolute است (نه بر اساس فعالیت)

### 3️⃣ **SessionTimeoutMiddleware جدید**
   - فایل: `phonix/middleware.py`
   - کار: بررسی فعالیت کاربر و logout خودکار بعد از 30 دقیقه

```python
class SessionTimeoutMiddleware(MiddlewareMixin):
    """بررسی زمان آخرین فعالیت و logout خودکار"""
```

### 4️⃣ **ترتیب Middleware**
```python
MIDDLEWARE = [
    # ...
    "phonix.middleware.SessionTimeoutMiddleware",  # اول
    "phonix.middleware.RoleBasedAccessMiddleware",  # دوم
    # ...
]
```

---

## تغییرات موارد 📋

### ✅ `phonix/settings.py`
- SESSION_COOKIE_AGE = 1800 (30 دقیقه)
- SESSION_SAVE_EVERY_REQUEST = False

### ✅ `phonix/middleware.py`
- اضافه: `SessionTimeoutMiddleware`
- فعال کردن بررسی فعالیت

### ✅ `core/views.py`
- تغییر: `index()` view
- حالا ریدایرکت به لاگین یا داشبورد می‌کند

---

## نحوه کار 🔐

```
1. کاربر ورود می‌کند
   └─> Session ساخته می‌شود + آخرین فعالیت ثبت می‌شود

2. کاربر کار می‌کند
   └─> هر درخواست: بررسی می‌شود آیا 30 دقیقه گذشته؟

3. بعد از 30 دقیقه:
   └─> SessionTimeoutMiddleware کاربر رو logout می‌کند
   └─> ریدایرکت به صفحه لاگین

4. کاربر باید دوباره لاگین کند
   └─> Session جدید ساخته می‌شود
```

---

## آزمایش 🧪

### تغییر Session Timeout برای آزمایش

در `settings.py` می‌توانید زمان را تغییر دهید:

```python
# 5 دقیقه (برای آزمایش)
SESSION_COOKIE_AGE = 300

# 30 دقیقه (پیش‌فرض)
SESSION_COOKIE_AGE = 1800

# 1 ساعت
SESSION_COOKIE_AGE = 3600
```

---

## اطلاعات مهم ⚠️

1. **Timeout Absolute:** کاربر حتی اگر کار می‌کند، بعد از 30 دقیقه logout می‌شود
2. **بدون صفحه Loading Static:** تمام صفحه اولیه اب Django است
3. **صفحه لاگین:** تمام کاربران ابتدا به صفحه لاگین می‌روند

---

## فایل‌های تغییر یافته 📁

- `phonix/settings.py` - تنظیمات Session
- `phonix/middleware.py` - Middleware جدید
- `core/views.py` - تغییر index view
- ❌ `index.html` - حذف شد
