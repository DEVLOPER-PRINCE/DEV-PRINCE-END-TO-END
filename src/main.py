"""
fbchat-v2 — Minimal Bot (Prince Malhotra)
=========================================

Ye bot `_core` / `_features` / `_messaging` teeno layers ko milake
ek simple command-driven chat bot banata hai jo groups aur DMs mein
kaam karta hai.

Supported Commands:
    /ping              -> "pong" reply karta hai (latency check)
    /help              -> commands ki list dikhata hai
    /id                -> sender ka threadID + userID print karta hai
    /echo <text>       -> jo text likho wahi repeat karta hai
    /search <keyword>  -> Facebook par user search karta hai
    /unsend            -> bot ka last message us thread mein unsend karta hai

Configuration:
    `config.json` file `main.py` ke saath isi folder mein banao:
        {
            "cookies": "c_user=...; xs=...; fr=...; datr=...;",
            "prefix":  "/",
            "admins":  ["1000xxxxxxxxxx"]
        }

@PrinceMalhotra | GitHub: PrinceMalhotra
"""

from __future__ import annotations

import json
import os
import sys
import time
import threading
import traceback
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Ensure `src/` is on sys.path when running this file directly
# ---------------------------------------------------------------------------
HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from _core._session import dataGetHome
from _features._facebook import _search
from _messaging._send import api as SendAPI
from _messaging._unsend import func as unsend_message
from _messaging._listening import listeningEvent
from _messaging._listening_e2ee import listeningE2EEEvent


# ---------------------------------------------------------------------------
# Config helpers
# ---------------------------------------------------------------------------

CONFIG_PATH = HERE / "config.json"


def load_config() -> dict:
    """config.json padho. Template banao agar exist nahi karta."""
    if not CONFIG_PATH.exists():
        template = {
            "cookies": "PASTE_YOUR_FACEBOOK_COOKIE_HERE",
            "prefix": "/",
            "admins": [],
        }
        CONFIG_PATH.write_text(
            json.dumps(template, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"[config] Template bana diya {CONFIG_PATH} par. "
              "'cookies' fill karo phir dobara chalao.")
        sys.exit(1)

    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        cfg = json.load(f)

    if not cfg.get("cookies") or "PASTE_YOUR" in cfg["cookies"]:
        print("[config] Facebook cookie config.json mein nahi bhara gaya hai.")
        sys.exit(1)

    cfg.setdefault("prefix", "/")
    cfg.setdefault("admins", [])
    return cfg


def log(tag: str, msg: str) -> None:
    print(f"[{datetime.now():%H:%M:%S}] [{tag}] {msg}")


# ---------------------------------------------------------------------------
# Bot
# ---------------------------------------------------------------------------

class SimpleBot:
    """Seedha-saada Bot — `listener.bodyResults` poll karo aur commands par reply karo."""

    def __init__(self, dataFB: dict, prefix: str = "/", admins: list | None = None):
        self.dataFB = dataFB
        self.prefix = prefix
        self.admins = set(map(str, admins or []))

        self.sender = SendAPI()
        self.listener = listeningEvent(dataFB)

        # E2EE listener for 1-to-1 DMs (Secret Conversations)
        self.e2ee_listener: listeningE2EEEvent | None = None

        # Processed messageIDs track karo → ek message ko 2 baar reply karne se bachao
        self._last_seen_message_id: str | None = None
        # Har thread mein bot ka last sent messageID store karo (for /unsend)
        self._last_bot_message: dict[str, str] = {}

        # Map prefix-less command -> handler
        self._handlers = {
            "ping":   self._cmd_ping,
            "help":   self._cmd_help,
            "id":     self._cmd_id,
            "echo":   self._cmd_echo,
            "search": self._cmd_search,
            "unsend": self._cmd_unsend,
        }

    # -- public ---------------------------------------------------------------

    def run(self) -> None:
        """Alag thread mein listener shuru karo aur events poll karo."""
        log("bot", f"Login with UID = {self.dataFB.get('FacebookID')}")
        self.listener.get_last_seq_id()

        # Regular MQTT listener (groups/threads)
        t = threading.Thread(
            target=self.listener.connect_mqtt,
            name="fbchat-listener",
            daemon=True,
        )
        t.start()
        log("bot", "Listener (group) shuru ho gaya.")

        # E2EE listener for 1-to-1 DMs
        self._start_e2ee_listener()

        log("bot", "Band karne ke liye Ctrl+C dabao.")
        try:
            while True:
                self._poll_once()
                time.sleep(0.3)
        except KeyboardInterrupt:
            log("bot", "User request par band kiya gaya.")

    def _start_e2ee_listener(self) -> None:
        """DM (1-to-1) ke liye E2EE listener shuru karo."""
        try:
            self.e2ee_listener = listeningE2EEEvent(
                self.dataFB,
                log_level="warn",
                e2ee_memory_only=True,
                enable_e2ee=True,
            )

            @self.e2ee_listener.on_message
            def on_e2ee_msg(evt):
                evt_type = evt.get("type")
                data = evt.get("data", {})

                if evt_type == "e2eeMessage":
                    body = data.get("body") or data.get("text") or data.get("content") or ""
                    sender_id = str(data.get("senderJid", "").split("@")[0])
                    chat_jid = data.get("chatJid", "")
                    msg_id = data.get("id", "")

                    if not body or sender_id == str(self.dataFB.get("FacebookID")):
                        return

                    log("e2ee", f"{sender_id}: {body!r}")

                    if not body.startswith(self.prefix):
                        return

                    without_prefix = body[len(self.prefix):].strip()
                    if not without_prefix:
                        return
                    parts = without_prefix.split(maxsplit=1)
                    cmd = parts[0].lower()
                    arg = parts[1] if len(parts) > 1 else ""

                    self._handle_e2ee_cmd(cmd, arg, data)

            t = threading.Thread(
                target=self.e2ee_listener.connect_mqtt,
                name="fbchat-e2ee-listener",
                daemon=True,
            )
            t.start()
            log("bot", "Listener (E2EE DM) shuru ho gaya.")

        except FileNotFoundError as e:
            log("bot", f"⚠️  E2EE bridge not found — DM listener disabled. {e}")
        except Exception as e:
            log("bot", f"⚠️  E2EE listener failed to start: {e}")

    def _handle_e2ee_cmd(self, cmd: str, arg: str, data: dict) -> None:
        """E2EE DM se commands handle karo."""
        chat_jid = data.get("chatJid", "")
        msg_id = data.get("id", "")
        sender_jid = data.get("senderJid", "")

        def reply(text: str):
            if self.e2ee_listener:
                self.e2ee_listener.send_e2ee_message(
                    chat_jid, text,
                    reply_to_id=msg_id,
                    reply_to_sender_jid=sender_jid,
                )
                log("e2ee-send", f"-> {chat_jid}: {text!r}")

        if cmd == "ping":
            reply("🏓 pong!")
        elif cmd == "help":
            p = self.prefix
            reply(
                "📖 Supported commands (E2EE DM):\n"
                f"• {p}ping   — connection check\n"
                f"• {p}help   — commands list\n"
                f"• {p}echo <text> — repeats your message\n"
                f"• {p}id     — show chat JID"
            )
        elif cmd == "echo":
            reply(arg if arg else f"Usage: {self.prefix}echo <your message>")
        elif cmd == "id":
            reply(f"🆔 chatJid: {chat_jid}\n   senderJid: {sender_jid}")

    # -- internal -------------------------------------------------------------

    def _poll_once(self) -> None:
        """bodyResults scan karo; agar nayi unprocessed message ho → dispatch karo."""
        snap = self.listener.bodyResults
        mid = snap.get("messageID")
        body = snap.get("body")

        if not mid or mid == self._last_seen_message_id:
            return
        self._last_seen_message_id = mid

        # Bot ke apne messages ignore karo
        sender_id = str(snap.get("userID") or "")
        if sender_id == str(self.dataFB.get("FacebookID")):
            return

        if not body:
            return

        log("recv", f"[{snap.get('type')}] {sender_id}@{snap.get('replyToID')}: {body!r}")

        if not body.startswith(self.prefix):
            return

        # Command alag karo
        without_prefix = body[len(self.prefix):].strip()
        if not without_prefix:
            return
        parts = without_prefix.split(maxsplit=1)
        cmd = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        handler = self._handlers.get(cmd)
        if handler is None:
            return  # unknown commands ke liye chup rehna

        try:
            handler(snap, arg)
        except Exception as exc:  # noqa: BLE001 - listener thread crash se bachao
            log("err", f"Command /{cmd} handle karte waqt error: {exc}")
            traceback.print_exc()

    # -- send wrapper ---------------------------------------------------------

    def _reply(self, snap: dict, content: str) -> None:
        thread_id = snap["replyToID"]
        type_chat = "user" if snap.get("type") == "user" else None

        result = self.sender.send(
            self.dataFB,
            content,
            thread_id,
            typeChat=type_chat,
            replyMessage=True,
            messageID=snap.get("messageID"),
        )

        if isinstance(result, dict) and result.get("success") == 1:
            try:
                self._last_bot_message[str(thread_id)] = (
                    result["payload"]["messageID"]
                )
            except (KeyError, TypeError):
                pass
            log("send", f"-> {thread_id}: {content!r}")
        else:
            log("send", f"FAIL -> {thread_id}: {result}")

    # -- commands -------------------------------------------------------------

    def _cmd_ping(self, snap: dict, arg: str) -> None:
        sent_ts = int(snap.get("timestamp") or 0)
        if sent_ts:
            latency_ms = max(0, int(time.time() * 1000) - sent_ts)
            self._reply(snap, f"🏓 pong! ({latency_ms} ms)")
        else:
            self._reply(snap, "🏓 pong!")

    def _cmd_help(self, snap: dict, arg: str) -> None:
        p = self.prefix
        self._reply(snap, (
            "📖 Supported commands:\n"
            f"• {p}ping            — latency check\n"
            f"• {p}help            — help dikhao\n"
            f"• {p}id              — threadID + userID dekho\n"
            f"• {p}echo <text>     — message repeat karo\n"
            f"• {p}search <word>   — Facebook par user dhundo\n"
            f"• {p}unsend          — bot ka last message unsend karo"
        ))

    def _cmd_id(self, snap: dict, arg: str) -> None:
        self._reply(snap, (
            f"🆔 type      : {snap.get('type')}\n"
            f"   threadID  : {snap.get('replyToID')}\n"
            f"   userID    : {snap.get('userID')}\n"
            f"   messageID : {snap.get('messageID')}"
        ))

    def _cmd_echo(self, snap: dict, arg: str) -> None:
        if not arg:
            self._reply(snap, f"Usage: {self.prefix}echo <your message>")
            return
        self._reply(snap, arg)

    def _cmd_search(self, snap: dict, arg: str) -> None:
        if not arg:
            self._reply(snap, f"Usage: {self.prefix}search <keyword>")
            return
        try:
            res = _search.func(self.dataFB, arg)
        except Exception as exc:  # noqa: BLE001
            self._reply(snap, f"❌ Search error: {exc}")
            return

        users = res.get("searchResultsDict") if isinstance(res, dict) else None
        if not users:
            self._reply(snap, f"🔍 Koi result nahi mila: {arg}")
            return

        lines = [f'Search results for "{arg}":']
        for i, u in enumerate(users[:5], 1):
            lines.append(f"{i}. {u.get('name')} — {u.get('id')}")
        self._reply(snap, "\n".join(lines))

    def _cmd_unsend(self, snap: dict, arg: str) -> None:
        # Agar admins configure hain toh sirf admins use kar sakte hain
        sender_id = str(snap.get("userID") or "")
        if self.admins and sender_id not in self.admins:
            self._reply(snap, "⛔ Sirf admins yeh command use kar sakte hain.")
            return

        thread_id = str(snap["replyToID"])
        target = self._last_bot_message.get(thread_id)
        if not target:
            self._reply(snap, "ℹ️ Is thread mein abhi tak koi unsend karne ke liye message nahi hai.")
            return

        result = unsend_message(target, self.dataFB)
        log("unsend", f"{target} -> {result}")
        # Unsend ke baad → woh ID bhool jao
        self._last_bot_message.pop(thread_id, None)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    cfg = load_config()

    log("boot", "Cookie se dataFB initialize ho raha hai…")
    dataFB = dataGetHome(cfg["cookies"])

    if not dataFB.get("FacebookID"):
        log("boot", "❌ FacebookID nahi mila — cookie expire ho gayi hogi.")
        sys.exit(1)

    bot = SimpleBot(
        dataFB,
        prefix=cfg["prefix"],
        admins=cfg["admins"],
    )
    bot.run()


if __name__ == "__main__":
    main()
 