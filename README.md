# Anime RSS Fetcher & Torrent Proxy

A compact **Flask** service that

* normalises and republishes selected Nyaa RSS feeds (SubsPlease 1080p & common English‑dub releases),
* exposes direct torrent‑download endpoints, and
* keeps itself awake via an asynchronous uptime pinger.

The repo ships with a **Dockerfile** and **Procfile**, so you can launch locally, in Docker, or in a single click on **Koyeb**.

---

## ✨ Key Features

| Feature                     | Details                                                                                                                                |
| --------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| 📰 **RSS Rebroadcast**      | `/rss/sub` and `/rss/dub` fetch Nyaa RSS, rewrite titles (season/episode detection) and rewrite torrent links to point to your server. |
| 📥 **Torrent Proxy**        | `/torrents/<id>.torrent` or `/torrents/<filename>` downloads the .torrent from Nyaa and streams it to the client.                      |
| 🔄 **Uptime Monitor**       | A background `aiohttp` task pings `URL_TO_MONITOR` every `CHECK_INTERVAL` seconds to stop free hosts from sleeping.                    |
| 🐳 **Docker & Koyeb‑ready** | Containerised build with tiniest footprint. One‑click deploy badge included.                                                           |

---

## 🗂️ Project Layout

```text
.
├── app.py            # Main Flask application (edit config here)
├── Dockerfile        # Python 3.12‑slim container spec
├── Procfile          # web: gunicorn app:app (example)
├── requirements.txt  # aiohttp, Flask, pattern, requests, etc.
└── README.md         # You’re reading it
```

---

## 🔧 Configuration (edit `app.py`)

```python
app = Flask(__name__)
app.secret_key = "REPLACE_ME"         # 👉 Mandatory – use env var in production

URL_TO_MONITOR = "https://example.com/"  # 👉 Site to ping for uptime
CHECK_INTERVAL = 360                     # 👉 Seconds between pings
```

You can hard‑code values or override with environment variables:

```bash
export SECRET_KEY="$(openssl rand -base64 32)"
export URL_TO_MONITOR="https://my‑frontend.vercel.app/"
export CHECK_INTERVAL=300
```

---

## 🚀 Quick Start (local venv)

```bash
# 1 Clone
git clone https://github.com/ArihantSharma/RSS_Auto.git
cd anime‑rss‑proxy

# 2 Python env
python3 -m venv .venv
source .venv/bin/activate

# 3 Deps
pip install -r requirements.txt

# 4 Config (optional – see above)

# 5 Run
python app.py  # http://127.0.0.1:5000
```

---

## 🐳 Run with Docker

```bash
# Build
docker build -t anime‑rss‑proxy .

# Run (port 8080 outside)
docker run -p 8080:5000 \ \
  -e SECRET_KEY="$(openssl rand -base64 32)" \ \
  -e URL_TO_MONITOR="https://my‑frontend.vercel.app/" \ \
  anime‑rss‑proxy
```

Now open **[http://localhost:8080/rss/sub](http://localhost:8080/rss/sub)**.

---

## ⚡ One‑Click Deploy to Koyeb

[![Deploy to Koyeb](https://www.koyeb.com/static/images/deploy/button.svg)](https://app.koyeb.com/deploy?type=git&repository=github.com/ArihantSharma/RSS_Auto&branch=main)

> During the wizard, add `SECRET_KEY`, `URL_TO_MONITOR`, and `CHECK_INTERVAL` in **Environment Variables**.

---

## 📚 API Reference

| Method | Path                   | Purpose                                                                     |
| ------ | ---------------------- | --------------------------------------------------------------------------- |
| `GET`  | `/`                    | Simple HTML index (template).                                               |
| `GET`  | `/rss/sub`             | Returns **SubsPlease 1080p** feed (first 30 items), with titles normalised. |
| `GET`  | `/rss/dub`             | Returns common English‑dub feed (first 30 items).                           |
| `GET`  | `/torrents/<int:id>`   | Streams the torrent whose Nyaa ID equals `id`.                              |
| `GET`  | `/torrents/<filename>` | Streams torrent file matching `filename` (e.g. `abc123.torrent`).           |

### Pagination

Right now the endpoints return **up to 30 items** (hard‑coded in `app.py`).  If you need classic ~~`?page=`/`?per_page=`~~ pagination, extend `fetch_and_parse_rss()`—the helper already slices to 30 items, so swapping that for a paginator is trivial.

---

## 🛠️ Extending & Hacking

* Add more RSS suppliers or switch to Jikan/MyAnimeList.
* Replace the naive background thread with **APScheduler**, **Celery** or **Quart** if you move to async Flask.
* Cache results with Redis to avoid hammering Nyaa.
* Unit‑test with `pytest` and automate via GitHub Actions.

---

## 📝 License

MIT — do what you like, just keep the copyright‐notice.

---

## 🙋 Support / Contributing

Pull requests are welcome!  Please:

1. Fork → feature branch → PR.
2. Follow PEP 8 + 120‑col style.
3. Add context and docs for new endpoints.

Enjoy & happy anime binge‑automation! 🎉
