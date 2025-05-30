# GehtSo - Internet Plan Comparator

GehtSo is a web application for comparing internet offers from multiple fictional providers in Germany. Enter your address to see and filter available plans, compare prices, speeds, contract durations, and more.

## 👋 Introduction

Before starting this project i have written less than 200 lines of code in Python. My goal was to complete the challenge using all available tools and (mostly) free services. I approached the task having no expectations on how far i would get into programming and finished it with a set of skills in full-stack development and a newfound passion.

## 🚀 Demo / Link

Live Website: [https://gehtso.onrender.com](https://gehtso.onrender.com)

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

```python
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

*Note:* Gunicorn is not available on Windows by default

6. **Open in your browser:**

[http://localhost:5000/](http://localhost:5000/)

## 📝 Usage

- Enter your address to fetch available offers.

- Use filters on the left to narrow down results.

- Click "Share via:" to generate a shareable link or send results via messaging platforms.

- Change pages to see more results.

## 💫 Features

- Compare offers from ByteMe, Ping Perfect, Servus Speed, VerbynDich, and WebWunder (fictional internet providers created for the CHECK24 Coding Challenge)
- Filter by speed, data limit, contract duration, TV, connection type, provider, installation included, and age
- Sort results by price, speed, or cost after two years
- Share results via WhatsApp, Messenger, Telegram, Email, or copy link
- Address autocomplete for PLZ and street using OpenStreetMap Nominatim
- Address validation
- Session state to remember user's last search
- Result caching: Internet offer results are cached for each address and provider. This speeds up repeated searches and reduces API calls. Cached results expire after 60 minutes
- Pagination: Results are split into pages for easier browsing. Changing filter state returns you to page 1.

## 🗂️ Project Structure

```plaintext
GehtSo/
├── src/
│   ├── app.py               # Flask application entry point
│   ├── compare_offers.py    # Offer aggregation and filtering logic
│   ├── utils.py             # Utility functions (API-safe strings, autocomplete)
│   ├── providers/           # Provider-specific fetchers
│   │   ├── fetch_byteme.py
│   │   ├── fetch_pingperfect.py
│   │   ├── fetch_servusspeed.py
│   │   ├── fetch_verbyndich.py
│   │   └── fetch_webwunder.py
│   ├── static/              # Static files (CSS, JS, images)
│   └── templates/           # HTML templates
├── tests/                   # Python tests
├── requirements.txt         # List of Python dependencies
├── Procfile                 # Heroku process file
├── .env                     # Environment variables
└── README.md                # Project documentation 
```

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

This will execute the code in each file’s `__main__` block, allowing you to check if fetching and parsing for that provider works as expected.

## ⚠️ Limitations

- I use only free hosting and services, so API calls may be slower or rate-limited. For a better experience run the programm locally.

- On Render’s free plan, web services spin down after 15 minutes of inactivity; the first request can experience a cold start delay of 50 seconds or more.

- **Cache is server-local:** Cached results are stored on the server's filesystem in the `cache/` directory. The cache is not shared between server instances and the cache may be lost if the server restarts.

- **Snapshots are stored as files:** Snapshots are saved as files in the `src/snapshots/` directory. Snapshots are not shared between deployments and may be lost if the server is redeployed or the filesystem is cleared.

## 🏁 Roadmap & Possible Improvements

- **Frontend Tests:** Add a test suite for the frontend to ensure UI components work as expected.

- **Responsive Design:** Improve the web UI to ensure usability on tablets and mobile devices.

- **Durable snapshot storage and lifecycle management:** Migrate from local file-based snapshot storage to a durable service (e.g., PostgreSQL or AWS S3) and implement snapshot lifecycle management (e.g., auto-delete snapshots older than 30 days).

## 💭 Why not OOP?

I chose a procedural approach over object-oriented programming (OOP) to keep the codebase clear and maintainable:

- Diverse APIs: Each provider uses a completely different method to access their API, returns different formats (CSV, JSON, SOAP), and uses inconsistent field names.

- Specialized parsing: Some providers embed data in plain-text descriptions or have their own voucher systems. Handling these cases in standalone functions avoids the extra layers of class abstractions.

- Focused output: The main objective is a single function that gathers and normalizes offers into a uniform structure. Procedural code lets me sequence each provider’s logic directly before producing the final result.

## 📃 License

MIT License

___
✨ Made by Adelina Batereanu for the CHECK24 Coding Challenge.
