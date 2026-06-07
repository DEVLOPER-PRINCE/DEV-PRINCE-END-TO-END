# 🚀 fbchat-v2 v2.1.0 — Messenger E2EE officially landed!

> *Release date: 2026-05-12*

> *Codename: **Labyrinth***

> *Author: ***Prince Malhotra***

Facebook ne E2EE Messenger par default enable kiya (11/2024) ke baad **18 mahine** baad, `fbchat-v2` aaj officially us capability ko **wapas unlock** karta hai — aur aapko sirf **1 import line badalni hai**.

---

## ✨ Highlights

### 🔓 E2EE Listener for 1-to-1 messages
- Nayi class [`listeningE2EEEvent`](src/_messaging/_listening_e2ee.py) — `listeningEvent` ka drop-in replacement.
- `bodyResults` **bilkul same schema** ke saath `_listening.py` jaisi (`body`, `timestamp`, `userID`, `messageID`, `replyToID`, `type`, `attachments.id`, `attachments.url`).
- Bonus: `e2eeBodyResults` mein Signal metadata (`chatJid`, `senderJid`).
- `type = "user" / "thread"` khud infer karta hai — aapke event handling code mein **kuch nahi badalna**.

### 🌉 Independent Go Bridge (`bridge-e2ee/`)
- Single-file Go binary (`fbchat-bridge-e2ee[.exe]`, ~25–40 MB) jo include karta hai:
  - **Signal Protocol** (Curve25519, Double Ratchet, Sender Keys, AES-GCM, HKDF, Noise XX) via `whatsmeow`.
  - **Meta Labyrinth / Lightspeed** via `mautrix-meta`.
- Python ↔ Go communication **JSON-RPC line-delimited** stdin/stdout se hoti hai.
- **Alag subprocess** mein chalta hai → bridge crash Python ko crash nahi karega.
- Path override env var `FBCHAT_E2EE_BIN` se kar sakte hain.

### 📚 Complete setup documentation
- README (VI + EN) mein §**Installation** ko **7 saaf steps** mein rewrite kiya, saath mein:
  - Extended requirements table (Python / Go / Git / RAM / Network).
  - Sanity check `python -c "import requests, paho.mqtt.client, attr, pyotp; print('OK')"`.
  - Smoke test `python src/main.py`.
- `_messaging` README mein **Separate Installation** + **Module Reference** section `_listening_e2ee.py` ke liye.
- `bridge-e2ee/` README mein complete RPC contract description.

---

## 🎯 Is update ki ahmiyat

| Pehle v2.1.0 | v2.1.0 se |
|---|---|
| Sirf group messages padh sakte the | **Group + 1-to-1 (E2EE) messages** dono padh sakte hain |
| `type` mein sirf legacy values | Abhi bhi `"user" / "thread"` — **breaking nahi** |
| Native dep build guide nahi thi | Step-by-step Go toolchain guide hai |
| Bridge prototype DLL/ctypes (crash risk) | **Subprocess JSON-RPC** safe, single exe mein package kiya ja sakta hai |

---

## 🚦 Quick Start (E2EE)

```powershell
# 1. Bridge ek baar build karo
cd fbchat-v2/bridge-e2ee
git clone https://github.com/mautrix/meta.git ./meta
go mod tidy
go build -ldflags="-s -w" -o ../build/fbchat-bridge-e2ee.exe .   # Windows
# Linux/macOS: .exe hatao
```

```python
# 2. _listening.py jaisa hi use karo
import threading
from _messaging._listening_e2ee import listeningE2EEEvent

listener = listeningE2EEEvent(dataFB)
listener.get_last_seq_id()

@listener.on_message
def handle(evt):
    print(listener.bodyResults)        # ← _listening.py jaisa schema
    print(listener.e2eeBodyResults)    # chatJid / senderJid

threading.Thread(target=listener.connect_mqtt, daemon=True).start()
```

> 💡 E2EE build nahi karna? `from _messaging._listening import listeningEvent` jaisa hi chalate raho — **kuch nahi badla**.

---

## 🔧 2.0.x se upgrade karna

- ✅ **`_listening.py` use karne wale code mein koi breaking change nahi**.
- 🆕 E2EE ke liye: Go ≥ 1.24 + Git install karo, binary ek baar build karo (README §Installation step 5 dekho).
- 🧹 `meta-messenger.js/` folder (agar tha) hata sakte hain — nayi bridge poori tarah independent hai.

```powershell
git pull
pip install -r requirements.txt   # koi nayi Python dep nahi, par chalana safe hai
```

---

## 📦 System Requirements

| Component | Minimum | Recommended | Notes |
|---|---|---|---|
| Python | 3.10 | 3.11 / 3.12 | Zaroori |
| Go | 1.24 | 1.24+ | Sirf E2EE ke liye |
| Git | any | latest | `mautrix/meta` clone karne ke liye |
| RAM | 256 MB | 1 GB+ | Bridge ~80–150 MB runtime par |
| OS | Windows / Linux / macOS | — | — |

---

## 🐛 Known Issues

- Bridge prebuilt binary Releases page par abhi available nahi hai — **local build karna padega**. Yeh [Roadmap](README.md) par agla item hai.
- Pehli `go mod tidy` ~300 MB module cache download karta hai — thoda sabr rakho.
- Kuch networks par `edge-chat.facebook.com` ka WebSocket connection throttle ho sakta hai → proxy use karo.

---

## 📝 Full Changelog

[CHANGELOG.md](CHANGELOG.md#210--2026-05-12) dekho.

**Diff compare:** [`v2.0.x...v2.1.0`](https://github.com/PrinceMalhotra/fbchat-v2/compare/v2.0.x...v2.1.0)

---

## 🙏 Shukriya

- Un sabhi users ka jo 18 mahine se Messenger E2EE enable hone ke baad intezar kar rahe the.
- [`mautrix/meta`](https://github.com/mautrix/meta) aur [`tulir/whatsmeow`](https://github.com/tulir/whatsmeow) projects — decryption ko possible banane ki bunyaad.
- [`yumi-team/meta-messenger.js`](https://github.com/yumi-team/meta-messenger.js) project — bridge design reference.
- Saare contributors jo [README §Contributors](README.md) mein listed hain.

---

<div align="center">

**📥 Download:** [Source code (zip)](https://github.com/PrinceMalhotra/fbchat-v2/archive/refs/tags/v2.1.0.zip) · [Source code (tar.gz)](https://github.com/PrinceMalhotra/fbchat-v2/archive/refs/tags/v2.1.0.tar.gz)

**💬 Questions & Bug Reports:** [GitHub Issues](https://github.com/PrinceMalhotra/fbchat-v2/issues) · [Telegram @PrinceMalhotra](https://t.me/PrinceMalhotra)

*Made with ❤️ by [Prince Malhotra](https://github.com/PrinceMalhotra)*

</div>
