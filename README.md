# GehtSo - Internet Plan Comparator

GehtSo is a web application for comparing internet offers from multiple fictional providers in Germany. Enter your address to see and filter available plans, compare prices, speeds, contract durations, and more.


## 🚀 Demo / Link

Live Website: [https://gehtso.onrender.com](https://gehtso.onrender.com)

**Note:** Provider servers will not be functional after July 2025.  
To see the demo, use the cache with one of the following addresses:

- Unter den Linden 77, 10117 Berlin
- Marienplatz 1, 80331 München
- Königsallee 14, 40212 Düsseldorf
- Mönckebergstraße 1, 20095 Hamburg
- Römerberg 23, 60311 Frankfurt am Main


## ⚙️ Setup

1. **Clone the repository:**

```bash
git clone https://github.com/AdelinaBatereanu/GehtSo.git
cd GehtSo
```

2. **Create and activate virtual environment:**

```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

4. **Set up environment variables:**

- Create a file named `.env` in the project root directory.
- Add your API keys and credentials for all providers to this file

*Note:* for your Flask App key you can use any random set of characters

```env
# Web Wunder
WEBWUNDER_API_KEY = "your_key_here"
# Verbyn Dich
VERBYNDICH_API_KEY = "your_key_here"
# Byte Me
BYTEME_API_KEY = "your_key_here"
# Servus Speed
SERVUSSPEED_USERNAME = "your_username_here"
SERVUSSPEED_PASSWORD = "your_password_here"
# Ping Perfect
PINGPERFECT_SIGNATURE_SECRET = "your_signature_here"
PINGPERFECT_CLIENT_ID = "your_id_here"
# Flask App
APP_SECRET_KEY = "your_random_key_here"
# Cache Time
CACHE_TIME = "in_seconds"
# Nominatim OpenStreetMap
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
HEADERS = {"User-Agent": "yourProjectTag (yourEmail@mail.com)"}
```

5. **Run the app locally:**

```bash
cd src
flask run
```

Or for production:

```bash
gunicorn app:app --chdir src --bind 0.0.0.0:8000
```

6. **Open in your browser:**

[http://localhost:5000/](http://localhost:5000/)


## 🗂️ Project Structure

```plaintext
GehtSo/
├── src/
│   ├── app.py                # Flask application entry point
│   ├── compare_offers.py     # Offer aggregation, filtering (backend), sorting (backend)
│   ├── providers/            # Provider-specific fetchers (class-based)
│   │   ├── base.py           # Base class for provider fetchers
│   │   ├── registry.py       # Dict of all provider fetchers
│   │   ├── fetch_byteme.py
│   │   ├── fetch_pingperfect.py
│   │   ├── fetch_servusspeed.py
│   │   ├── fetch_verbyndich.py
│   │   └── fetch_webwunder.py
│   ├── utils/                # Utility modules (autocomplete, validation, cache, etc.)
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   └── templates/            # HTML templates
├── cache/                    # Cached provider results
├── tests/                    # Python tests
├── requirements.txt
├── .env
└── README.md
```


## 📝 Usage

- Enter your address to fetch available offers
- Use filters on the left to narrow down results
- Click "Share via:" to generate a shareable link or send results via messaging platforms
- Change pages to see more results


## 💫 Features

- Compare offers from multiple providers (fictional internet providers created for the CHECK24 Coding Challenge)
- Filter by speed, data limit, contract duration, TV, connection type, provider, installation included, and age
- Sort results by price, speed, or cost after two years
- Share results via WhatsApp, Messenger, Telegram, Email, or copy link
- Address autocomplete and validation
- Session state to remember user's last search
- Result caching for faster repeated searches
- Pagination for easier browsing


## ⚠️ Limitations

- Provider APIs will be offline after July 2025; only cached addresses will work for demo.
- Cache and snapshots are stored locally and are not shared between server instances.
- API calls may be rate-limited or slow on free hosting.
- Demo link can experience a cold start delay of 50 seconds or more.

## 🏁 Roadmap & Possible Improvements

- Add frontend tests for UI components.
- Improve responsive design for mobile/tablet
- Migrate snapshot and cache storage to a durable backend (e.g., database or cloud storage)


## ✅ Testing

To run the test suite, make sure you are in the project root.
  
The project includes a `pytest.ini` file that adds `src` to the Python path, so you can run:

```bash
pytest
```

*Note:* For `/share`, the tests will create files in the `snapshots` folder.

To test provider fetching logic individually (for developement and debugging) run:

```bash
python src/providers/fetch_byteme.py
python src/providers/fetch_pingperfect.py
# ...etc.
```


## 📃 License

MIT License

---

✨ Made by Adelina Batereanu for the CHECK24 Coding Challenge.
