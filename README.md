# IO - AI Assistant (Django + Gemini + PWA)

IO is a class assistant web app built with Django and the Google Gemini API. It is a Progressive Web App: it can be installed on supported devices and shows an offline notice when the connection is lost.

## Features
- Chat with Gemini through a Django backend (the API key never reaches the browser)
- Conversation memory within a session
- Online / Thinking / Offline status indicator
- Installable PWA with a web app manifest and service worker

## Run locally
1. Create and activate a virtual environment, then install packages:
   pip install -r requirements.txt
2. Copy .env.example to .env and add your own Gemini API key from Google AI Studio.
3. Start the server:
   python manage.py runserver
4. Open http://127.0.0.1:8000

## Tech stack
Django, HTML, CSS, Bootstrap, JavaScript, Google Gemini API, service worker, web app manifest.

## Security note
Never commit your .env file. It is listed in .gitignore.
