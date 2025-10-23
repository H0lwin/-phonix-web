# 📋 خلاصه تغییرات - Session Timeout و صفحة اولیه جنگو

## 🎯 هدف
1. **حذف صفحة HTML static** - `index.html` دیگر استفاده نمی‌شود
2. **پیاده‌سازی Session Timeout** - کاربران هر 30 دقیقه باید دوباره لاگین کنند
3. **صفحة لاگین اجباری** - تمام کاربران ابتدا باید لاگین کنند

---

## ✅ تغییرات انجام شده

### 1️⃣ **`phonix/settings.py`**
```python
# تغییرات Session
SESSION_COOKIE_AGE = 1800              # 30 دقیقه
SESSION_SAVE_EVERY_REQUEST = False     # Timeout absolute
```

**دلیل:**
- `SESSION_COOKIE_AGE = 1800`: کاربر بعد از 30 دقیقه logout می‌شود
- `SESSION_SAVE_EVERY_REQUEST = False`: timeout تازه‌سازی نمی‌شود (حتی با فعالیت)

**Middleware اضافه شد:**
```python
MIDDLEWARE = [
    # ...
    "phonix.middleware.SessionTimeoutMiddleware",  # بررسی timeout
    "phonix.middleware.RoleBasedAccessMiddleware",
    # ...
]
```

---

### 2️⃣ **`phonix/middleware.py` - SessionTimeoutMiddleware جدید**
```python
class SessionTimeoutMiddleware(MiddlewareMixin):
    """
    بررسی فعالیت کاربر و logout خودکار بعد از SESSION_COOKIE_AGE
    """
    def process_request(self, request):
        if request.user.is_authenticated:
            # بررسی آیا بیش از 30 دقیقه بدون فعالیت است
            if '_last_activity' in request.session:
                # مقایسه زمان و logout خودکار اگر لازم باشد
            
            # ثبت زمان فعالیت
            request.session['_last_activity'] = time.time()
```

---

### 3️⃣ **`core/views.py` - تغییر index() view**

**قبل:**
```python
def index(request):
    """صفحه static HTML"""
    return render(request, 'index.html', context)
```

**بعد:**
```python
def index(request):
    """ریدایرکت خودکار به داشبورد یا لاگین"""
    if request.user.is_authenticated:
        # ریدایرکت به داشبورد مناسب بر اساس نقش
        if role == 'admin':
            return redirect('admin:index')
        elif role == 'lawyer':
            return redirect('lawyer_admin:index')
        elif role == 'employee':
            return redirect('employee_admin:index')
    
    # اگر لاگین نشده: ریدایرکت به صفحه لاگین
    return redirect('core:login')
```

---

### 4️⃣ **`templates/error.html` - صفحة خطا جدید**
- صفحة خطای حرفه‌ای برای 404 و 500
- طراحی جذاب و واکنش‌پذیر
- دکمه‌های بازگشت

---

### 5️⃣ **`core/views.py` - بروزرسانی صفحات خطا**
```python
def page_not_found(request, exception):
    """صفحه 404"""
    return render(request, 'error.html', {
        'error': 'صفحه یافت نشد',
        'status_code': 404
    }, status=404)

def server_error(request):
    """صفحه 500"""
    return render(request, 'error.html', {
        'error': 'خطای سرور',
        'status_code': 500
    }, status=500)
```

---

### 6️⃣ **`phonix/urls.py` - handlers صفحات خطا**
```python
from core.views import page_not_found, server_error

# صفحات خطا
handler404 = page_not_found
handler500 = server_error
```

---

## 🔄 جریان کار جدید

```
1. کاربر بر روی "/" کلیک می‌کند
   ↓
2. Django index() view رو فراخوانی می‌کند
   ↓
3. بررسی: آیا کاربر لاگین شده؟
   ├─ اگر بله: ریدایرکت به داشبورد مناسب
   └─ اگر نه: ریدایرکت به صفحه لاگین
   ↓
4. کاربر لاگین می‌کند
   ↓
5. session شروع می‌شود (30 دقیقه timeout)
   ↓
6. SessionTimeoutMiddleware بررسی می‌کند
   ├─ اگر فعال: timeout تازه‌سازی نمی‌شود
   └─ بعد از 30 دقیقه: logout خودکار
   ↓
7. کاربر باید دوباره لاگین کند
```

---

## ⚙️ تنظیمات Session

| تنظیم | مقدار | توضیح |
|------|-------|--------|
| `SESSION_COOKIE_AGE` | 1800 | 30 دقیقه |
| `SESSION_SAVE_EVERY_REQUEST` | False | timeout تازه‌سازی نمی‌شود |
| `SESSION_EXPIRE_AT_BROWSER_CLOSE` | False | بر اساس timeout |
| `SESSION_COOKIE_HTTPONLY` | True | محافظت شده از JavaScript |
| `SESSION_COOKIE_SAMESITE` | Strict | CSRF protection |

---

## 🧪 آزمایش

### برای تغییر timeout (آزمایش)
در `settings.py` تغییر دهید:
```python
SESSION_COOKIE_AGE = 300  # 5 دقیقه برای آزمایش
SESSION_COOKIE_AGE = 1800 # 30 دقیقه (پیش‌فرض)
```

### آزمایش Session Timeout
1. لاگین کنید
2. 30 دقیقه (یا تغییر یافته) صبر کنید یا در `settings.py` SESSION_COOKIE_AGE را کاهش دهید
3. صفحه رو refresh کنید
4. ✅ باید به صفحة لاگین ریدایرکت شوید

---

## 📁 فایل‌های تغییر یافته

| فایل | تغییرات |
|------|--------|
| ✅ `phonix/settings.py` | SESSION_COOKIE_AGE و MIDDLEWARE |
| ✅ `phonix/middleware.py` | SessionTimeoutMiddleware اضافه |
| ✅ `phonix/urls.py` | handlers صفحات خطا |
| ✅ `core/views.py` | index() view و صفحات خطا |
| ✅ `templates/error.html` | صفحة خطا جدید (ایجاد شد) |
| ❌ `templates/index.html` | دیگر استفاده نمی‌شود |

---

## ⚠️ نکات مهم

1. **Timeout Absolute:** کاربران حتی اگر کار می‌کنند، بعد از 30 دقیقه logout می‌شوند
2. **عدم Static Landing Page:** صفحة اولیه دیگر static نیست
3. **Mandatory Login:** تمام کاربران باید لاگین کنند
4. **Session Security:** تنظیمات بالای امنیتی برای session
5. **Error Handling:** صفحات خطا بهتر طراحی شدند

---

## 🚀 مراحل نهایی

1. ✅ تغییرات انجام شدند
2. ✅ Middleware فعال شد
3. ✅ صفحات خطا درست شدند
4. ⏳ **بعد از بروزرسانی:**
   - تمام کاربران لاگین شده خود‌کار logout می‌شوند
   - کاربران نیاز دارند دوباره لاگین کنند

---

## 📞 سوالات متداول

**Q: کاربر فعال باید logout شود؟**
A: بله! SESSION_SAVE_EVERY_REQUEST = False است، بنابراین timeout absolute است.

**Q: چگونه می‌توانم timeout را تغییر دهم؟**
A: `SESSION_COOKIE_AGE` را در `settings.py` تغییر دهید (بر حسب ثانیه).

**Q: آیا صفحة index.html حذف شود؟**
A: نه، برای صفحات خطا استفاده می‌شود، اما صفحة اولیه دیگر آن نیست.
