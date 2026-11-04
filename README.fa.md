# OrthoMUI Telegram Bot — نسخه مناسب میزبانی آنلاین

این نسخه از webhook استفاده می‌کند تا روی سرویس میزبانی وب اجرا شود. فایل‌های `app.py`, `content.json`, `requirements.txt`, `render.yaml` را به مخزن GitHub خصوصی منتقل کنید و در Render متصل کنید.

## تنظیمات Render
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`
- Environment variables: `TELEGRAM_BOT_TOKEN` = توکن BotFather؛ `WEBHOOK_SECRET` = رشته تصادفی محرمانه
- پس از deploy، آدرس سرویس را کپی کنید. سپس webhook را با این آدرس تنظیم کنید:
  `https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook?url=<YOUR_RENDER_URL>/telegram-webhook&secret_token=<YOUR_WEBHOOK_SECRET>`
  جایگزین‌ها را فقط در مرورگر خودتان وارد کنید؛ URL حاوی توکن محرمانه است و نباید به اشتراک گذاشته شود. پاسخ باید شامل `"ok":true` باشد.

## محدودیت
Render free web services ممکن است در دوره بی‌ترافیکی به خواب بروند و برای بات حیاتی/تولیدی تضمین پایداری ندارند. این بسته برای تست اولیه مناسب است. محتوای نمونه هنوز باید با مطالب و تصاویر واقعی سایت جایگزین شود.
