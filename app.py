That **405 Not Allowed** means Flask is receiving the request but rejecting the method. Most likely cause: Flask is redirecting `/download` → `/download/` and the redirect turns POST into GET, which your route doesn't accept.

**Quick fix — open `app.py` and change this line:**

```python
# BEFORE
@app.route('/download', methods=['POST'])

# AFTER
@app.route('/download', methods=['POST'], strict_slashes=False)
```

**Also double-check these 3 things:**

**1. Your folder structure must be exactly:**
```
aj-downloader/
├── app.py
├── templates/
│   └── index.html    ← must be inside templates/
└── downloads/
```

**2. Make sure Flask is actually running** — your terminal should show:
```
* Running on http://127.0.0.1:5000
```

**3. Open the site at exactly:**
```
http://127.0.0.1:5000
```
Not `localhost/download` directly — always go through the homepage first.

---

**If it still doesn't work**, add this debug route to `app.py` temporarily to confirm Flask is receiving the POST:

```python
@app.route('/download', methods=['GET', 'POST'], strict_slashes=False)
def download_video():
    if request.method == 'GET':
        return "Send a POST request", 400
    # ... rest of your code
```

Try that and let me know what error shows up next — we'll squash it!
