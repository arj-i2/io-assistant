import json, os, time, requests
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie

MODELS = ["gemini-3.8-flash", "gemini-3.5-flash-lite"]
RETRY_CODES = {429, 500, 503, 504}

SYSTEM = (
    "You are IO, a friendly and clear AI class assistant for students. "
    "Explain things in simple terms, use short paragraphs, and use bullet points "
    "or numbered steps when helpful. Keep answers concise unless asked for detail."
)

FRIENDLY = {
    503: "IO is a little busy right now. Please try again in a few seconds.",
    500: "Gemini had a hiccup. Please try again in a moment.",
    504: "Gemini took too long to respond. Please try again.",
    429: "Too many requests at once. Please wait a minute and try again.",
    403: "The API key was rejected. Check GEMINI_API_KEY in your .env file.",
    404: "The Gemini model name was not found. Check MODELS in views.py.",
}

@ensure_csrf_cookie
def index(request):
    return render(request, "chat/index.html")

def service_worker(request):
    return render(request, "chat/sw.js", content_type="application/javascript")

def call_gemini(payload):
    key = os.getenv("GEMINI_API_KEY", "")
    last = None
    for model in MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        for attempt in range(2):
            try:
                r = requests.post(url, headers={"x-goog-api-key": key}, json=payload, timeout=45)
            except requests.RequestException:
                last = None
                time.sleep(1.5 * (attempt + 1))
                continue
            if r.status_code == 200:
                return r, None
            last = r.status_code
            if r.status_code not in RETRY_CODES:
                return r, r.status_code
            time.sleep(1.5 * (attempt + 1))
    return None, last

@require_POST
def ask(request):
    body = json.loads(request.body)
    prompt = body.get("prompt", "").strip()
    if not prompt:
        return JsonResponse({"error": "Empty prompt"}, status=400)

    history = body.get("history", [])[-10:]
    contents = [
        {
            "role": "user" if h.get("role") == "user" else "model",
            "parts": [{"text": str(h.get("text", ""))}],
        }
        for h in history
    ]
    contents.append({"role": "user", "parts": [{"text": prompt}]})

    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM}]},
        "contents": contents,
    }

    r, err = call_gemini(payload)
    if r is None or r.status_code != 200:
        msg = FRIENDLY.get(err, "IO could not reach Gemini. Please try again.")
        return JsonResponse({"error": msg}, status=502)

    try:
        text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        return JsonResponse({"error": "IO could not answer that one. Try rephrasing."}, status=502)
    return JsonResponse({"reply": text})
