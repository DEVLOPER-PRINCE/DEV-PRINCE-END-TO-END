"""
Prince E2EE Convo — Web UI Backend
===================================
Flask server for the message-sender web interface.
"""
from __future__ import annotations

import hashlib
import json
import os
import queue
import secrets
import sys
import threading
import time
from datetime import datetime
from functools import wraps
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from flask import (
    Flask,
    Response,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    stream_with_context,
    url_for,
)

from _core._facebookLogin import loginFacebook
from _core._session import dataGetHome
from _messaging._send import api as SendAPI

# ── App ──────────────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", secrets.token_hex(32))

CONFIG_PATH = HERE / "config.json"
ACCOUNTS_PATH = HERE / "accounts.json"

# ── Config helpers ───────────────────────────────────────────────────────

def load_config() -> dict:
    if CONFIG_PATH.exists():
        with CONFIG_PATH.open(encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_config(cfg: dict) -> None:
    with CONFIG_PATH.open("w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


# ── Account helpers ───────────────────────────────────────────────────────

def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def load_accounts() -> dict:
    if ACCOUNTS_PATH.exists():
        with ACCOUNTS_PATH.open(encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_accounts(accounts: dict) -> None:
    with ACCOUNTS_PATH.open("w", encoding="utf-8") as f:
        json.dump(accounts, f, indent=2, ensure_ascii=False)


def accounts_exist() -> bool:
    return bool(load_accounts())


# ── Global state ─────────────────────────────────────────────────────────
_state: dict = {
    "running": False,
    "paused": False,
    "loop": False,
    "dataFB": None,
    "fb_logged_in": False,
    "fb_user_id": "",
    "sent_count": 0,
    "total_count": 0,
}
_lock = threading.Lock()
_log_q: queue.Queue = queue.Queue(maxsize=1000)

# ── Logger ───────────────────────────────────────────────────────────────

def log(msg: str, level: str = "INFO") -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    entry = f"[{ts}] [{level}] {msg}"
    print(entry, flush=True)
    try:
        _log_q.put_nowait(entry)
    except queue.Full:
        try:
            _log_q.get_nowait()
        except queue.Empty:
            pass
        _log_q.put_nowait(entry)


# ── Auth decorator ───────────────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not session.get("logged_in"):
            if request.is_json or request.path.startswith("/api/") or request.path == "/stream":
                return jsonify({"error": "Unauthorized"}), 401
            # No accounts yet → go register first
            if not accounts_exist():
                return redirect(url_for("register_page"))
            return redirect(url_for("login_page"))
        return f(*args, **kwargs)
    return wrapped


# ── Pages ────────────────────────────────────────────────────────────────

@app.route("/register")
def register_page():
    if session.get("logged_in"):
        return redirect(url_for("index"))
    return render_template("register.html")


@app.route("/login")
def login_page():
    if session.get("logged_in"):
        return redirect(url_for("index"))
    if not accounts_exist():
        return redirect(url_for("register_page"))
    return render_template("login.html")


@app.route("/")
@login_required
def index():
    return render_template("index.html", username=session.get("username", "user"))


# ── Auth API ─────────────────────────────────────────────────────────────

@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.json or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")
    confirm  = data.get("confirm", "")

    if not username or not password:
        return jsonify({"success": False, "error": "Username aur password zaroori hain"})
    if len(username) < 3:
        return jsonify({"success": False, "error": "Username kam se kam 3 characters ka hona chahiye"})
    if len(password) < 6:
        return jsonify({"success": False, "error": "Password kam se kam 6 characters ka hona chahiye"})
    if password != confirm:
        return jsonify({"success": False, "error": "Dono passwords match nahi kar rahe"})

    accounts = load_accounts()
    if username in accounts:
        return jsonify({"success": False, "error": f"'{username}' username already le liya gaya hai"})

    accounts[username] = _hash(password)
    save_accounts(accounts)
    log(f"✅ Naya account ban gaya: {username}")
    return jsonify({"success": True, "username": username})


@app.route("/api/auth", methods=["POST"])
def auth():
    data = request.json or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")

    accounts = load_accounts()
    if not accounts:
        return jsonify({"success": False, "error": "Pehle account banao /register par"}), 401

    stored = accounts.get(username)
    if stored and stored == _hash(password):
        session["logged_in"] = True
        session["username"] = username
        return jsonify({"success": True, "username": username})
    return jsonify({"success": False, "error": "Galat username ya password"}), 401


@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True})


# ── Facebook Login API ───────────────────────────────────────────────────

@app.route("/api/fb-login", methods=["POST"])
@login_required
def fb_login():
    data = request.json or {}
    method = data.get("method", "cookie")

    try:
        if method == "cookie":
            cookies = data.get("cookies", "").strip()
            if not cookies:
                return jsonify({"success": False, "error": "Cookie string empty hai"})
            log("Cookie se Facebook login ho raha hai...")
            dataFB = dataGetHome(cookies)
        else:
            email = data.get("email", "").strip()
            password = data.get("password", "").strip()
            if not email or not password:
                return jsonify({"success": False, "error": "Email/password empty hai"})
            log(f"Email se login: {email}")
            result = loginFacebook(email, password).main()
            if "error" in result:
                err = result["error"]
                msg = err.get("description") or err.get("title") or "Login failed"
                return jsonify({"success": False, "error": msg})
            cookies = result["success"]["setCookies"]
            log("Facebook login successful! Session cookie mil gayi.")
            dataFB = dataGetHome(cookies)

        fb_id = dataFB.get("FacebookID", "")
        if not fb_id or "Unable" in str(fb_id):
            return jsonify({
                "success": False,
                "error": "Facebook ID nahi mila — cookie expire ho gayi hogi",
            })

        with _lock:
            _state["dataFB"] = dataFB
            _state["fb_logged_in"] = True
            _state["fb_user_id"] = fb_id

        cfg = load_config()
        cfg["cookies"] = cookies
        save_config(cfg)

        log(f"✅ Facebook login OK! UID: {fb_id}")
        return jsonify({"success": True, "uid": fb_id})

    except Exception as exc:
        log(f"Login exception: {exc}", "ERROR")
        return jsonify({"success": False, "error": str(exc)})


# ── Sender controls ──────────────────────────────────────────────────────

@app.route("/api/start", methods=["POST"])
@login_required
def start_sending():
    data = request.json or {}

    with _lock:
        if not _state["fb_logged_in"] or not _state["dataFB"]:
            return jsonify({"success": False, "error": "Pehle Facebook login karo (Cookies tab)"})
        if _state["running"]:
            return jsonify({"success": False, "error": "Already chal raha hai"})

    thread_id_raw = data.get("thread_id", "").strip()
    name = data.get("name", "").strip()
    messages_raw = data.get("messages", "")
    delay = max(0.5, float(data.get("delay", 3)))
    loop = bool(data.get("loop", False))

    if not thread_id_raw:
        return jsonify({"success": False, "error": "Thread / User ID daalo"})

    messages = [m.strip() for m in messages_raw.split("\n") if m.strip()]
    if not messages:
        return jsonify({"success": False, "error": "Kam se kam ek message daalo"})

    if thread_id_raw.endswith("@g.us"):
        thread_id = thread_id_raw.replace("@g.us", "").strip()
        type_chat = None
    elif "@" in thread_id_raw:
        thread_id = thread_id_raw.split("@")[0].strip()
        type_chat = None
    else:
        thread_id = thread_id_raw
        type_chat = data.get("type_chat", None)

    with _lock:
        _state["running"] = True
        _state["paused"] = False
        _state["loop"] = loop
        _state["sent_count"] = 0
        _state["total_count"] = len(messages)
        dataFB = _state["dataFB"]

    t = threading.Thread(
        target=_sender_worker,
        args=(dataFB, thread_id, name, messages, delay, loop, type_chat),
        daemon=True,
    )
    t.start()

    log(f"🚀 Sending shuru! Thread: {thread_id} | Messages: {len(messages)} | Delay: {delay}s | Loop: {loop}")
    return jsonify({"success": True})


@app.route("/api/pause", methods=["POST"])
@login_required
def pause_sending():
    with _lock:
        if not _state["running"]:
            return jsonify({"success": False, "error": "Chal nahi raha"})
        _state["paused"] = not _state["paused"]
        paused = _state["paused"]
    log(f"{'⏸ Paused' if paused else '▶ Resumed'}!")
    return jsonify({"success": True, "paused": paused})


@app.route("/api/stop", methods=["POST"])
@login_required
def stop_sending():
    with _lock:
        _state["running"] = False
        _state["paused"] = False
    log("⏹ Sending band kar diya!")
    return jsonify({"success": True})


@app.route("/api/loop", methods=["POST"])
@login_required
def toggle_loop():
    with _lock:
        _state["loop"] = not _state["loop"]
        loop = _state["loop"]
    log(f"🔄 Loop {'ON' if loop else 'OFF'} kar diya!")
    return jsonify({"success": True, "loop": loop})


@app.route("/api/status")
@login_required
def get_status():
    with _lock:
        return jsonify({
            "running": _state["running"],
            "paused": _state["paused"],
            "loop": _state["loop"],
            "fb_logged_in": _state["fb_logged_in"],
            "fb_user_id": _state["fb_user_id"],
            "sent_count": _state["sent_count"],
            "total_count": _state["total_count"],
        })


# ── SSE Stream ───────────────────────────────────────────────────────────

@app.route("/stream")
@login_required
def stream():
    def generate():
        while True:
            try:
                msg = _log_q.get(timeout=1)
                yield f"data: {json.dumps({'log': msg})}\n\n"
            except queue.Empty:
                yield f"data: {json.dumps({'ping': 1})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


# ── Sender worker thread ─────────────────────────────────────────────────

def _sender_worker(
    dataFB: dict,
    thread_id: str,
    name: str,
    messages: list[str],
    delay: float,
    loop_mode: bool,
    type_chat,
) -> None:
    sender = SendAPI()
    idx = 0
    total = len(messages)

    log(f"Worker tayaar: {total} messages, {delay}s delay, loop={'on' if loop_mode else 'off'}")

    while True:
        with _lock:
            running = _state["running"]
            paused = _state["paused"]
            loop = _state["loop"] or loop_mode

        if not running:
            log("Worker band ho gaya.")
            break

        if paused:
            time.sleep(0.3)
            continue

        if idx >= total:
            if loop:
                idx = 0
                log("🔄 Loop: saare messages reset ho gaye, fir se shuru!")
                continue
            else:
                log("✅ Saare messages bhej diye gaye!")
                with _lock:
                    _state["running"] = False
                break

        msg = messages[idx]
        if name:
            if "{name}" in msg:
                msg = msg.replace("{name}", name)
            else:
                msg = f"{name} {msg}"

        try:
            result = sender.send(dataFB, msg, thread_id, typeChat=type_chat)
            with _lock:
                _state["sent_count"] = idx + 1
            if result.get("success") == 1:
                preview = msg[:55] + ("…" if len(msg) > 55 else "")
                log(f"✓ [{idx + 1}/{total}] Bheja: {preview}")
            else:
                pl = result.get("payload", {})
                log(f"✗ [{idx + 1}/{total}] Error: {pl}", "ERROR")
        except Exception as exc:
            log(f"✗ Exception msg {idx + 1}: {exc}", "ERROR")

        idx += 1

        elapsed = 0.0
        while elapsed < delay:
            with _lock:
                if not _state["running"]:
                    return
            time.sleep(0.1)
            elapsed += 0.1


# ── Startup auto-login ───────────────────────────────────────────────────

def _auto_login() -> None:
    cfg = load_config()
    cookies = cfg.get("cookies", "")
    if not cookies or "PASTE_YOUR" in cookies:
        return
    try:
        log("Saved cookie se auto-login ho raha hai...")
        dataFB = dataGetHome(cookies)
        fb_id = dataFB.get("FacebookID", "")
        if fb_id and "Unable" not in str(fb_id):
            with _lock:
                _state["dataFB"] = dataFB
                _state["fb_logged_in"] = True
                _state["fb_user_id"] = fb_id
            log(f"✅ Auto-login OK! UID: {fb_id}")
        else:
            log("⚠ Auto-login: cookie expire ho gayi, phir se login karo", "WARN")
    except Exception as exc:
        log(f"⚠ Auto-login failed: {exc}", "WARN")


# ── Main ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    threading.Thread(target=_auto_login, daemon=True).start()
    port = int(os.environ.get("PORT", 5000))
    log(f"🌐 Web UI shuru ho raha hai port {port} par...")
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
