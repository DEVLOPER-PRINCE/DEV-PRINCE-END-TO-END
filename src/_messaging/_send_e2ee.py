"""
fbchat-v2 :: _send_e2ee.py
==========================

Facebook Messenger mein **E2EE encrypted** (Secret Conversations / Labyrinth)
messages bhejne ke liye Go binary ``fbchat-bridge-e2ee`` ka use karta hai.

Ye module ``_BridgeProcess`` class aur ``_listening_e2ee.py`` ka binary
discovery logic **share** karta hai — listener ke bridge ko **reuse karna**
recommend kiya jata hai, nayi process spawn karne ki bajay (har process ko
Meta ke saath dubara pair karna padta hai).

Do modes mein use karo:

1. **Reuse** (recommended) — fast, pair dobara nahi karna::

       from _messaging._listening_e2ee import listeningE2EEEvent
       from _messaging._send_e2ee import api as E2EESender

       listener = listeningE2EEEvent(dataFB)
       threading.Thread(target=listener.connect_mqtt, daemon=True).start()
       # ... "e2eeConnected" event ka wait karo ...

       sender = E2EESender(listener=listener)
         sender.send(chat_jid="100012345678@msgr", contentSend="pong")
         sender.send_to_user("100012345678", "Facebook ID se directly message karo")

2. **Standalone** — khud bridge spawn karo, khud ``connect()`` + ``connect_e2ee()``::

       sender = E2EESender(dataFB=dataFB, log_level="warn")
       sender.connect()           # blocking pairing handshake
         sender.send(chat_jid="100012345678", contentSend="hello")  # auto → 100012345678@msgr
       sender.close()

``send(...)`` API ``_send.py`` ka style follow karta hai — dict return karta hai
``{"success": 1, ...}`` ya ``{"error": 1, ...}`` ke form mein.

Reference: meta-messenger.js · ``Client.sendE2EEMessage()``.

Author: Prince Malhotra
"""

from __future__ import annotations

import datetime
from pathlib import Path
from typing import Any, Optional

from _messaging._listening_e2ee import (
    BridgeError,
    _BridgeProcess,
    _resolve_binary,
    parse_cookie_string,
    listeningE2EEEvent,
    _REQUIRED_COOKIES,
)


E2EE_MESSENGER_SERVER = "msgr"


def _resolve_device_path(device_path: str | None) -> str | None:
    if not device_path:
        return None
    path = Path(device_path).expanduser()
    if not path.is_absolute():
        path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    return str(path)


def normalize_chat_jid(target: str | int, *, default_server: str = E2EE_MESSENGER_SERVER) -> str:
    """Facebook user ID ya JID ko Messenger E2EE chat JID mein normalize karo.

    Messenger E2EE events ``chatJid`` ``<facebook_id>@msgr`` format mein return karte hain.
    Proactively bhejte waqt caller ke paas usually sirf Facebook numeric ID hota hai; yeh helper
    ``"100012345678"`` ko ``"100012345678@msgr"`` mein convert karta hai. Agar caller ne
    pehle se ``"100012345678@msgr"`` jaisa full JID diya hai toh same rakhta hai.
    """
    target_str = str(target or "").strip()
    if not target_str:
        raise ValueError("E2EE bhejne ke liye chat_jid ya Facebook user ID missing hai.")

    if target_str.lower().startswith(("fbid:", "facebook:")):
        target_str = target_str.split(":", 1)[1].strip()

    if "@" in target_str:
        return target_str

    if not target_str.isdigit():
        raise ValueError(
            "chat_jid full JID (`<id>@msgr`) ya Facebook numeric ID hona chahiye. "
            f"Jo mila: {target!r}"
        )

    server = (default_server or E2EE_MESSENGER_SERVER).strip().lstrip("@")
    return f"{target_str}@{server}"


def chat_jid_from_user_id(user_id: str | int) -> str:
    """``normalize_chat_jid(user_id)`` ka clear alias."""
    return normalize_chat_jid(user_id)


# ---------------------------------------------------------------------------
# Public sender
# ---------------------------------------------------------------------------

class api:
    """Sender E2EE — ``_send.api`` jaisa lekin Secret Conversations ke liye.

    Initialization:
        - ``api(listener=...)``  → ``listeningE2EEEvent`` ka bridge reuse karo
          (recommended; pairing nahi lagta).
        - ``api(dataFB=..., **opts)``  → alag bridge spawn karo. ``send()`` se pehle
          ``connect()`` call karna zaroori hai.

    Example::

        sender = api(listener=listener)
        result = sender.send(
            chat_jid="100012345678",
            contentSend="pong",
            replyMessage="3EB0...",                      # optional
            replySenderJid="100087...@msgr",             # optional (if reply)
        )
        sender.send_to_user("100012345678", "proactively message karo")
        # → {"success": 1, "payload": {"messageID": "...", "timestamp": ...}}
        # ya {"error": 1, "payload": {"error-decription": "...", "error-code": "..."}}
    """

    # ------------------------------------------------------------------
    def __init__(self,
                 listener: Optional[listeningE2EEEvent] = None,
                 dataFB: Optional[dict] = None,
                 *,
                 log_level: str = "none",
                 device_path: Optional[str] = None,
                 e2ee_memory_only: bool = True,
                 binary_path: Optional[str] = None) -> None:

        if listener is None and dataFB is None:
            raise ValueError(
                "`listener=` (reuse) YA `dataFB=` (standalone) dena zaroori hai."
            )
        if listener is not None and dataFB is not None:
            raise ValueError(
                "Sirf `listener=` YA `dataFB=` do, dono saath nahi."
            )

        self._listener = listener
        self._owns_bridge = listener is None     # standalone → sender khud band karta hai

        # Standalone-only state
        self.dataFB = dataFB
        self.log_level = log_level
        self.device_path = device_path
        self.e2ee_memory_only = e2ee_memory_only
        self._binary_path_override = binary_path
        self._bridge: Optional[_BridgeProcess] = None
        self._connected = False

        # Compat fields like _send.api
        self.results: dict[str, Any] = {}
        self.chat_jid = None
        self.content = None
        self.replyToId = None
        self.replyToSenderJid = None

    # ------------------------------------------------------------------
    @property
    def bridge(self) -> _BridgeProcess:
        """Abhi use ho raha bridge lo (listener ka ya sender ka khud ka)."""
        if self._listener is not None:
            br = self._listener._bridge
            if br is None:
                raise RuntimeError(
                    "Listener connect nahi hua — send se pehle listener.connect_mqtt() "
                    "call karo (usually daemon thread mein)."
                )
            return br
        if self._bridge is None:
            raise RuntimeError(
                "Standalone sender connect nahi hua — pehle sender.connect() call karo."
            )
        return self._bridge

    # ------------------------------------------------------------------
    def connect(self, *, enable_e2ee: bool = True, timeout: float = 120.0) -> dict[str, Any]:
        """Standalone mode: bridge spawn karo + Meta se pair karo."""
        if self._listener is not None:
            raise RuntimeError("connect() sirf standalone mode ke liye hai.")
        if self._connected:
            return {"already": True}

        binary = (
            Path(self._binary_path_override)
            if self._binary_path_override else _resolve_binary()
        )
        self._bridge = _BridgeProcess(binary)

        cks = parse_cookie_string(self.dataFB["cookieFacebook"])
        missing = [c for c in _REQUIRED_COOKIES if c not in cks]
        if missing:
            self._bridge.close()
            self._bridge = None
            raise ValueError(f"E2EE ke liye zaroori cookie missing: {missing}")
        keep = {"c_user", "xs", "datr", "fr", "sb", "wd", "presence"}
        cookies = {k: v for k, v in cks.items() if k in keep}

        cfg: dict[str, Any] = {
            "cookies": cookies,
            "platform": "facebook",
            "logLevel": self.log_level,
            "e2eeMemoryOnly": self.e2ee_memory_only,
        }
        device_path = _resolve_device_path(self.device_path)
        if device_path:
            cfg["devicePath"] = device_path

        self._bridge.call("newClient", cfg)
        info = self._bridge.call("connect", timeout=timeout)
        if enable_e2ee:
            self._bridge.call("connectE2EE", timeout=timeout)
        self._connected = True
        print(f"[{datetime.datetime.now()}] E2EE sender ready "
              f"(user={(info.get('user') or {}).get('id')})")
        return info

    # ------------------------------------------------------------------
    def send(self, chat_jid: str | int, contentSend: str,
             replyMessage: str = "",
             replySenderJid: str | int = "",
             timeout: float = 180.0) -> dict[str, Any]:
        """1 E2EE text message bhejo.

        :param chat_jid: Destination JID, e.g. Messenger JID
                 ``"100012345678@msgr"``.
                         Facebook numeric ID ``"100012345678"`` bhi de sakte ho;
                         module khud ``"100012345678@msgr"`` mein convert kar lega.
        :param contentSend: Text content.
        :param replyMessage: Reply karne wale message ka ID (optional).
        :param replySenderJid: Original message sender ka JID (reply ke liye zaroori).
        :return: Dict with same schema as ``_send.api.send``::

                    {"success": 1,
                     "payload": {"messageID": str, "timestamp": int}}

                 or::

                    {"error": 1,
                     "payload": {"error-decription": str, "error-code": str}}
        """
        try:
            normalized_chat_jid = normalize_chat_jid(chat_jid)
            normalized_reply_sender_jid = (
                normalize_chat_jid(replySenderJid) if replySenderJid else ""
            )
        except ValueError as exc:
            self.results = {
                "error": 1,
                "payload": {
                    "error-decription": str(exc),
                    "error-code": "invalid_chat_jid",
                },
            }
            return self.results

        # Instance mein store karo debug/log ke liye like _send.api
        self.chat_jid = normalized_chat_jid
        self.content = str(contentSend)
        self.replyToId = replyMessage or ""
        self.replyToSenderJid = normalized_reply_sender_jid

        try:
            data = self.bridge.call("sendE2EEMessage", {
                "chatJid": self.chat_jid,
                "text": self.content,
                "replyToId": self.replyToId,
                "replyToSenderJid": self.replyToSenderJid,
            }, timeout=timeout)
        except BridgeError as exc:
            self.results = {
                "error": 1,
                "payload": {
                    "error-decription": str(exc),
                    "error-code": "bridge_error",
                },
            }
            return self.results
        except RuntimeError as exc:
            self.results = {
                "error": 1,
                "payload": {
                    "error-decription": str(exc),
                    "error-code": "not_connected",
                },
            }
            return self.results

        # Bridge SendMessageResult return karta hai: {messageId, timestampMs, ...}
        self.results = {
            "success": 1,
            "payload": {
                "messageID": data.get("messageId") or data.get("id"),
                "timestamp": data.get("timestampMs") or data.get("timestamp") or 0,
            },
        }
        return self.results

    # ------------------------------------------------------------------
    def send_to_user(self, user_id: str | int, contentSend: str,
                     replyMessage: str = "",
                     replySenderJid: str | int = "",
                     timeout: float = 180.0) -> dict[str, Any]:
        """Facebook numeric ID par proactively message bhejo.

        ``user_id="100012345678"`` ko convert kiya jaayega
        ``chat_jid="100012345678@msgr"`` — bridge call karne se pehle.
        """
        return self.send(
            chat_jid=chat_jid_from_user_id(user_id),
            contentSend=contentSend,
            replyMessage=replyMessage,
            replySenderJid=replySenderJid,
            timeout=timeout,
        )

    # ------------------------------------------------------------------
    def reply(self, evt_data: dict, contentSend: str) -> dict[str, Any]:
        """Helper: ``e2eeMessage`` event ke ``data`` se directly reply karo.

        ::

            @listener.on_message
            def handler(evt):
                if evt["type"] == "e2eeMessage" and evt["data"]["text"] == "ping":
                    sender.reply(evt["data"], "pong")
        """
        return self.send(
            chat_jid=evt_data.get("chatJid", ""),
            contentSend=contentSend,
            replyMessage=evt_data.get("id", ""),
            replySenderJid=evt_data.get("senderJid", ""),
        )

    # ------------------------------------------------------------------
    def close(self) -> None:
        """Bridge band karo agar sender khud ka hai (standalone mode)."""
        if self._owns_bridge and self._bridge is not None:
            self._bridge.close()
            self._bridge = None
            self._connected = False

    def __enter__(self) -> "api":
        if self._owns_bridge and not self._connected:
            self.connect()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
