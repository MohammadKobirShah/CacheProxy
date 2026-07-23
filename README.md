# 🌐 Universal Caching Proxy Server

**Deploy on Render/Railway/Heroku - যেকোনো website cache করো, data save করো, fast browsing করো!**

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-green?logo=flask&logoColor=white)
![Deploy](https://img.shields.io/badge/Deploy-Render/Railway-purple)

---

## 🚀 Quick Deploy

### Option 1: Render (Recommended - Free Tier)

1. **Fork/Clone this repo**

2. **Go to [render.com](https://render.com)**

3. **New → Web Service**

4. **Connect your GitHub repo**

5. **Settings:**
   - **Name:** `caching-proxy`
   - **Runtime:** `Python`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 app:app`

6. **Create Web Service**

7. **Done!** Your proxy is live at `https://caching-proxy.onrender.com`

---

### Option 2: Railway

1. **Fork/Clone this repo**

2. **Go to [railway.app](https://railway.app)**

3. **New Project → Deploy from GitHub**

4. **Select your repo**

5. **Railway auto-detects Python and deploys!**

6. **Done!** Your proxy is live at `https://your-app.up.railway.app`

---

### Option 3: Heroku

```bash
# Login to Heroku
heroku login

# Create app
heroku create your-caching-proxy

# Deploy
git push heroku main

# Open
heroku open
```

---

## 📖 How to Use

### Step 1: Get Your Proxy URL

After deployment, you'll get a URL like:
- Render: `https://caching-proxy.onrender.com`
- Railway: `https://your-app.up.railway.app`

### Step 2: Configure Browser

**Chrome (with Extension - Easiest):**
1. Install [Proxy SwitchyOmega](https://chrome.google.com/webstore/detail/proxy-switchyomega/padekgcemlokbadohgkifijomclgjgif)
2. Create new profile
3. HTTP Proxy: `your-app-url` Port: `443` (or `80`)
4. Enable proxy when needed

**Firefox:**
1. Settings → Network Settings
2. Manual Proxy Configuration
3. HTTP Proxy: `your-app-url` Port: `443`
4. Check "Also use for HTTPS"

**System-Wide (Mac):**
```bash
export http_proxy=http://your-app-url
export https_proxy=http://your-app-url
```

**System-Wide (Windows):**
```powershell
$env:HTTP_PROXY="http://your-app-url"
$env:HTTPS_PROXY="http://your-app-url"
```

### Step 3: Browse!

Visit any website - it's now cached! Check stats at `your-app-url/stats`

---

## 🎯 API Endpoints

| Endpoint | Description |
|----------|-------------|
| `/` | Main proxy (pass URL in path) |
| `/stats` | Statistics dashboard |
| `/health` | Health check |
| `/cache/clear` | Clear all cache |
| `/cache/list` | List cached items |

### Usage Examples

**Direct URL access:**
```
https://your-app.onrender.com/https://arena.ai
```

**Stats page:**
```
https://your-app.onrender.com/stats
```

**Clear cache:**
```bash
curl https://your-app.onrender.com/cache/clear
```

---

## ⚙️ Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8080` | Server port (auto-set by platform) |
| `MAX_CACHE_SIZE_MB` | `500` | Maximum cache size in MB |
| `CACHE_TTL` | `3600` | Cache time-to-live in seconds |

**Set on Render:**
Dashboard → Environment → Add Variable

**Set on Railway:**
Dashboard → Variables → New Variable

---

## 📊 Features

- ✅ **Cache any website** - not just arena.ai!
- ✅ **80%+ bandwidth savings**
- ✅ **Fast on slow internet**
- ✅ **Beautiful stats dashboard**
- ✅ **Gzip/Brotli compression**
- ✅ **Auto cache eviction** (LRU)
- ✅ **Health checks** for uptime monitoring
- ✅ **Free tier compatible**

---

## 🔧 Local Development

```bash
# Clone
git clone <your-repo>
cd caching-proxy

# Install
pip install -r requirements.txt

# Run
python app.py

# Open
http://localhost:8080/stats
```

---

## 📁 Project Structure

```
caching-proxy/
├── app.py              # Main application
├── requirements.txt    # Python dependencies
├── Procfile           # Railway/Heroku config
├── render.yaml        # Render config
└── README.md          # This file
```

---

## 🛡️ Security Notes

- Don't store sensitive data in cache
- Use environment variables for config
- Consider adding authentication for production use
- Monitor usage via `/stats`

---

## 📈 Performance Tips

1. **Increase cache size** for heavy browsing
2. **Use multiple workers** for better concurrency
3. **Monitor hit rate** - aim for 60%+
4. **Clear cache periodically** if memory is limited

---

## 🤝 Contributing

1. Fork the repo
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open Pull Request

---

## 📄 License

MIT License - Use freely!

---

**Built by ENI for LO** 💙

*স্লো ইন্টারনেট? কোনো সমস্যা নেই! তোমার নিজের caching server এখন cloud-এ!*
