"""
fbchat-v2 :: tester.py
======================

`_listening_e2ee.py` (bridge Go subprocess) ka test driver.

Istemal ka tarika:
    1. Bridge build karo:
        cd fbchat-v2/bridge-e2ee
        git clone https://github.com/mautrix/meta.git ./meta
        go mod tidy
        go build -ldflags="-s -w" -o ../build/fbchat-bridge-e2ee.exe .

    2. Facebook cookie fbchat-v2/src/config.json mein daalo (key "cookies")
       ya env set karo FBCHAT_COOKIE="c_user=...; xs=...; datr=...; fr=...;"

    3. Chalao:
        python tester.py

Yeh bot:
    - Bridge se milne wale har event ko print karta hai.
    - "ping" message milne par "pong" bhejta hai (regular ya E2EE source ke hisaab se).
    - Band karne ke liye Ctrl+C.
"""

from __future__ import annotations

import json
import os
import signal
import sys
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Ensure src/ package can be imported
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from _core._session import dataGetHome  # noqa: E402
from _messaging._listening_e2ee import (  # noqa: E402
    BridgeError,
    listeningE2EEEvent,
    _resolve_binary,
)


# ---------------------------------------------------------------------------
# Cookie loader
# ---------------------------------------------------------------------------

def load_cookie() -> str:
    _ = json.loads(open("config.json", "r", encoding="utf-8").read())
    cookie = os.getenv("FBCHAT_COOKIE") or _["cookies"]
    if not cookie:
        raise ValueError("Facebook cookie nahi diya gaya! FBCHAT_COOKIE env set karo ya config.json mein daalo.")
    return cookie;


# ---------------------------------------------------------------------------
# Pretty printer
# ---------------------------------------------------------------------------

def ts() -> str:
    return datetime.now().strftime("%H:%M:%S")


def short(obj, n: int = 200) -> str:
    s = json.dumps(obj, ensure_ascii=False, default=str)
    return s if len(s) <= n else s[:n] + "…"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print(f"[{ts()}] tester.py shuru ho raha hai")

    # 1. Binary exist karti hai check karo
    try:
        binary = _resolve_binary()
        print(f"[{ts()}] bridge binary : {binary}")
    except FileNotFoundError as exc:
        sys.exit(str(exc))

    # 2. Cookie + dataFB lo
    cookie = load_cookie()
    print(f"[{ts()}] login ho raha hai...")
    try:
        dataFB = dataGetHome(cookie)
    except Exception as exc:  # noqa: BLE001
        sys.exit(f"dataGetHome fail hua: {exc}")

    fb_id = dataFB.get("FacebookID")
    print(f"[{ts()}] FacebookID = {fb_id}")

    # 3. Listener initialize karo
    listener = listeningE2EEEvent(
        dataFB,
        log_level="warn",
        e2ee_memory_only=True,   # persist ke liye False + device_path=... karo
        enable_e2ee=True,
    )

    @listener.on_message
    def handler(evt: dict) -> None:
        etype = evt.get("type")
        data = evt.get("data") or {}
        print(f"[{ts()}] <{etype}> {short(data)}")

        # Auto-reply "ping" -> "pong"
        text = (data.get("text") or "").strip().lower()
        if text != "ping":
            return

        sender_id = data.get("senderId")
        if str(sender_id) == str(fb_id):
            return  # apni hi message ignore karo

        try:
            if etype == "e2eeMessage":
                listener.send_e2ee_message(
                    data["chatJid"], "pong",
                    reply_to_id=data.get("id", ""),
                    reply_to_sender_jid=data.get("senderJid", ""),
                )
                print(f"[{ts()}] -> pong bheja (E2EE)")
            elif etype == "message":
                listener.send_message(
                    int(data["threadId"]), "pong",
                    reply_to_id=data.get("id", ""),
                )
                print(f"[{ts()}] -> pong bheja (regular)")
        except BridgeError as exc:
            print(f"[{ts()}] pong send fail: {exc}")

    # 4. Ctrl+C se cleanly exit karo
    def _sigint(_signum, _frame):
        print(f"\n[{ts()}] Ctrl+C mila, band ho raha hai...")
        listener.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, _sigint)

    # 5. Blocking loop
    try:
        listener.connect_mqtt()
    except KeyboardInterrupt:
        listener.stop()
    except Exception as exc:  # noqa: BLE001
        print(f"[{ts()}] serious error: {exc}")
        listener.stop()
        raise


if __name__ == "__main__":
    main()
