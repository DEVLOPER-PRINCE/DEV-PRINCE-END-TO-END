# `_messaging` — Messaging Layer

> Har Messenger action: bhejana, edit karna, realtime receive karna, file upload, react, vapas lena, theme badalna, message requests.

[![Layer](https://img.shields.io/badge/layer-messaging-EC4899)](.)
[![Status](https://img.shields.io/badge/status-stable-22c55e)](.)
[![English](https://img.shields.io/badge/docs-English-blue)](README_EN.md)

---

## 📑 Vishay Suchi

- [Kaam](#-kaam)
- [Setup](#-setup)
- [Directory Structure](#-directory-structure)
- [Public API](#-public-api)
- [`dataFB` Contract](#-datafb-contract)
- [Module Reference](#-module-reference)
  - [`_send.py`](#sendpy)
  - [`_editMessage.py`](#editmessagepy)
  - [`_send_e2ee.py`](#send_e2eepy)
  - [`_listening.py`](#listeningpy)
  - [`_listening_e2ee.py`](#listening_e2eepy)
  - [`_attachments.py`](#attachmentspy)
  - [`_reactions.py`](#reactionspy)
  - [`_changeTheme.py`](#changethemepy)
  - [`_unsend.py`](#unsendpy)
  - [`_message_requests.py`](#message_requestspy)
  - [`_createNotes.py`](#createnotespy)
- [Dependency Diagram](#-dependency-diagram)
- [Udaaharan](#-udaaharan)
- [Samasya Samadhan](#-samasya-samadhan)

---

## 🎯 Kaam

`_messaging` Messenger endpoints ko Python functions/classes mein wrap karta hai. Yeh layer session/token **handle nahi karta** (`_core` karta hai):

- 📤 User ya thread ko text message bhejna.
- ✏️ MQTT LS task se bheja hua message edit karna.
- 📎 Messenger se bhejna ke liye file upload karna.
- 📡 **MQTT over WebSocket** se realtime events sunna.
- ❤️ Reaction add / remove karna.
- 🎨 Thread Messenger ka theme / background badalna.
- ↩️ Bheja hua message vapas lena.
- 📥 **Message Requests** (pending messages) ki list lena.
- 📝 **Messenger Notes** (24h status-type note) manage karna: check / create / delete / recreate.

---

## 📦 Setup

`_messaging` `fbchat-v2` source code ke saath aata hai — alag install karne ki zaroorat nahi. Yeh section sirf runtime mein **kya chahiye** woh batata hai.

### 1. Python Dependencies (`requirements.txt` mein already hain)

| Package | Istemal | Note |
|---|---|---|
| `requests` | `_send` · `_attachments` · `_reactions` · `_unsend` · `_message_requests` · `_createNotes` · `_changeTheme` | HTTP client |
| `paho-mqtt` | `_listening` · `_editMessage` · `_changeTheme` | MQTT over WebSocket / LS task |
| `attrs` | `_listening` | Decorator class |

Sirf `_messaging` use karne ke liye quick install:

```bash
pip install requests paho-mqtt attrs
```

### 2. `_listening_e2ee` ke liye Go Bridge (optional)

Sirf tab chahiye jab aap 1-1 E2EE messages sunne ke liye `listeningE2EEEvent` use karo. **Go ≥ 1.24** + **Git** zaroori hai.

```bash
cd ../../bridge-e2ee            # fbchat-v2/src/_messaging/ se
git clone https://github.com/mautrix/meta.git ./meta
go mod tidy

# Windows
go build -ldflags="-s -w" -o ../build/fbchat-bridge-e2ee.exe .
# Linux / macOS
go build -ldflags="-s -w" -o ../build/fbchat-bridge-e2ee .
```

Python wrapper binary is order mein dhundta hai:

1. Environment variable `FBCHAT_E2EE_BIN` (agar set hai).
2. `fbchat-v2/build/fbchat-bridge-e2ee[.exe]` (default).

Binary nahi mili to `_listening_e2ee` `FileNotFoundError` raise karta hai with build instructions.

### 3. `_core` se `dataFB`

`_messaging` ke saare functions `_core._session.dataGetHome(setCookies)` se generate `dataFB` lete hain — dekho [`_core/README.md`](../_core/README.md#-datafb-contract).

Poori installation guide (clone, venv, Go toolchain, smoke test): dekho [README § Setup](../../README.md#-setup).

---

## 📂 Directory Structure

```text
src/_messaging/
├── __init__.py
├── _attachments.py        # File upload → attachmentID
├── _changeTheme.py        # Messenger thread theme / background badalna
├── _createNotes.py        # Messenger Notes (24h status): check/create/delete/recreate
├── _editMessage.py        # MQTT LS task se bheja hua message edit karna
├── _listening.py          # MQTT realtime listener (group messages)
├── _listening_e2ee.py     # Go Bridge — E2EE listener (1-1 messages)
├── _message_requests.py   # Pending messages
├── _reactions.py          # Reaction add / remove
├── _send.py               # Message bhejna (HTTP)
├── _send_e2ee.py          # Go Bridge — E2EE sender (1-1 Secret Conversations)
├── _unsend.py             # Message vapas lena
├── README.md              # ← aap yahan hain
└── README_EN.md
```

---

## 📦 Public API

```python
# src/_messaging/__init__.py
__all__ = [
    "_attachments", "_changeTheme", "_createNotes", "_editMessage",
    "_listening", "_listening_e2ee", "_reactions", "_send",
    "_send_e2ee", "_unsend", "_message_requests",
]
```

Har module ko `_messaging._send`, `_messaging._listening`, … se import karo.

---

## 🧩 `dataFB` Contract

`_messaging` ke saare APIs **`dataFB`** lete hain — jo `_core._session.dataGetHome(setCookies)` se generate hota hai.

Aam fields: `fb_dtsg` · `jazoest` · `FacebookID` · `clientRevision` · `cookieFacebook`.

> 📖 Poora schema: [`_core/README.md`](../_core/README.md#-datafb-contract).

---

## 📚 Module Reference

### `_send.py`

#### `class api`

Main message sending module.

```python
api().send(
    dataFB,
    contentSend,
    threadID,
    typeAttachment=None,
    attachmentID=None,
    typeChat=None,
    replyMessage=None,
    messageID=None,
)
```

| Parameter | Vivaran |
|---|---|
| `contentSend` | Message ka content. |
| `threadID` | Group ya user ID jispe bhejna hai. |
| `typeChat` | `"user"` 1-1 ke liye, `None` thread/group ke liye. |
| `typeAttachment` | `"gif"` · `"image"` · `"video"` · `"file"` · `"audio"`. |
| `attachmentID` | `_attachments` se upload ki gayi file ka ID. |
| `replyMessage` + `messageID` | Reply flow ke liye. |

**Return:**

- ✅ `{ "success": 1, "payload": { "messageID": ..., "timestamp": ... } }`
- ❌ `{ "error": 1, "payload": { "error-decription": ..., "error-code": ... } }`

> 📝 Module automatically `offline_threading_id`, `message_id`, `threading_id` generate karta hai. `/messaging/send/` response mein `for (;;);` prefix hota hai — already split kar diya gaya hai.

---

### `_editMessage.py`

MQTT LS task `queue_name="edit_message"` se bheja hua message edit karna.

```python
from _messaging import _editMessage

_editMessage.editMessage(dataFB, messageID="mid.$abc...", newText="Naya content")

# Ya unified entry point:
_editMessage.func(dataFB, "mid.$abc...", "Naya content")
```

| Function | Vivaran |
|---|---|
| `editMessage(dataFB, messageID, newText, timeout=20)` | Message edit karne ke liye LS task publish karna. |
| `func(dataFB, messageID, newText, timeout=20)` | fbchat-v2 module style mein alias. |

**Return:**

- ✅ `{ "success": 1, "messages": "...", "data": { "messageID": ..., "text": ... } }`
- ❌ `{ "error": 1, "messages": "...", "payload": {...} }`

> ⚠️ Facebook aam taur par sirf current account ke bheje messages edit karne deta hai.
> Yahan success matlab LS task `/ls_req` par publish hua; server phir bhi reject kar sakta hai
> agar message bahut purana hai ya account ko edit karne ka haq nahi.

---

### `_send_e2ee.py`

#### `class api`

`_send.api` ka E2EE version — Go bridge (`fbchat-bridge-e2ee`) ke zariye
1-1 (Secret Conversations) mein text message bhejna. Return schema
**bilkul wahi** hai jo `_send.api.send` ka hai, isliye calling code mein alag branch nahi chahiye.

Do initialization modes:

```python
# A) Listener ka bridge reuse karo — ZYAADA BEHTAR.
#    Dobara pair nahi karna, "new device login" notification nahi aata.
sender = api(listener=listeningE2EEEvent_instance)

# B) Standalone — alag bridge spawn karo.
sender = api(
    dataFB=dataFB,
    log_level="warn",
    device_path=None,        # Signal keys persist karne ke liye path + e2ee_memory_only=False daalo
    e2ee_memory_only=True,
    binary_path=None,        # auto-resolve build/fbchat-bridge-e2ee[.exe]
)
sender.connect()             # blocking pairing — sirf standalone ke liye
```

| Method | Vivaran |
|---|---|
| `send(chat_jid, contentSend, replyMessage="", replySenderJid="")` | 1 E2EE text message bhejna. `chat_jid` Messenger JID `<facebook_id>@msgr` ya sirf Facebook numeric ID ho sakta hai; module apne aap `@msgr` mein normalize karta hai. Group `threadID` **mat** pass karo. |
| `send_to_user(user_id, contentSend, replyMessage="", replySenderJid="")` | Facebook numeric ID se proactively bhejna, jaise `send_to_user("100012345678", "hello")`. |
| `reply(evt_data, contentSend)` | Helper: quote-reply ke liye event listener se `chatJid`, `id`, `senderJid` apne aap nikalata hai. |
| `connect(*, enable_e2ee=True, timeout=120)` | Sirf standalone. Bridge par `newClient` → `connect` → `connectE2EE` call karta hai. |
| `close()` | Sirf standalone. Apna bridge subprocess band karta hai. |
| `__enter__` / `__exit__` | Standalone `with` ke saath — apne aap `connect()` + `close()`. |

**Return** — [`_send.py`](#sendpy) jaisa hi schema:

- ✅ `{ "success": 1, "payload": { "messageID": ..., "timestamp": ... } }`
- ❌ `{ "error": 1, "payload": { "error-decription": ..., "error-code": "bridge_error" | "not_connected" } }`

> ⚠️ E2EE media bhejna (`SendE2EEImage` / `Video` / `Audio`) Go bridge mein hai
> lekin Python wrapper mein **abhi tak** expose nahi hua — abhi sirf text bhejna kaam karta hai.

---

### `_listening.py`

#### `class listeningEvent(dataFB)`

**MQTT over WebSocket** (`wss://edge-chat.facebook.com/...`) se realtime events sunna.

| Method | Vivaran |
|---|---|
| `get_last_seq_id()` | Nayi `last_seq_id` lena aur update karna. |
| `connect_mqtt()` | MQTT client shuru karna, sync queue subscribe karna, message delta receive karna. **Blocking** (`loop_forever()`). |

**Event aane par** — `self.bodyResults` mein:

```text
body · timestamp · userID · messageID · replyToID · type
attachments.id · attachments.url
```

**Highlights:**

- Anormal disconnect par **reconnect** mechanism hai.
- `errorCode == 100` (queue overflow) ko queue token reset karke handle karta hai.
- `connect_mqtt()` blocking hai → **alag thread / process** mein chalao.

---

### `_listening_e2ee.py`

#### `class listeningE2EEEvent(dataFB, *, log_level="none", binary=None)`

Go binary `fbchat-bridge-e2ee` ke zariye **E2EE** (1-1) messages sunna. Return schema **bilkul wahi** hai jo [`_listening.py`](#listeningpy) ka hai taaki aap 1-1 swap kar sako bina logic badlaaye.

| Method | Vivaran |
|---|---|
| `get_last_seq_id()` | `last_seq_id` console par print karna (`_listening.py` se parity). |
| `connect_mqtt()` | Bridge spawn karna, login karna, E2EE messages receive karna. **Blocking**. |
| `on_message(fn)` | Decorator/handler: `dict` event receive karne wala callback (already decrypt). |
| `stop()` | Bridge band karna aur subprocess close karna. |

**Event aane par** — `self.bodyResults` mein `_listening.py` jaisi fields:

```text
body · timestamp · userID · messageID · replyToID · type
attachments.id · attachments.url
```

Signal metadata ke liye `self.e2eeBodyResults`: `chatJid` · `senderJid`.

**Requirements:**

- Binary `fbchat-v2/build/fbchat-bridge-e2ee[.exe]` ya env `FBCHAT_E2EE_BIN` se.
- Build guide: [`bridge-e2ee/README.md`](../../bridge-e2ee/README.md).

---

### `_attachments.py`

```python
_uploadAttachment(filenames, dataFB)
```

`https://upload.facebook.com/ajax/mercury/upload.php` par file upload karna `attachmentID` lene ke liye.

**Return:**

```python
{
    "attachmentID": ...,
    "attachmentUrl": ...,
    "attachmentType": ...,
    "attachmentDataSend": None,
}
```

> ⚠️ Ek call = ek file. Error par function exception raise karne ki jagah console par print karta hai.

---

### `_reactions.py`

```python
func(dataFB, typeAdded, messageID, emojiChoice)
```

Message par reaction add / remove karna.

| Parameter | Values |
|---|---|
| `typeAdded` | `"add"` add karne ke liye; koi bhi aur value remove ke liye. |
| `messageID` | React karne wale message ka ID. |
| `emojiChoice` | Use karna wala emoji. |

**Return:** Raw `requests.Response` — aapko `response.text` khud parse karna padega.

---

### `_changeTheme.py`

Messenger themes ki list lena aur MQTT LS tasks se thread ka theme / background badalna. Yeh module `ws3-fca/theme.js` ka fbchat-v2 style port hai.

```python
from _messaging import _changeTheme

_changeTheme.listThemes(dataFB)
_changeTheme.findTheme(dataFB, "love")
_changeTheme.changeTheme(dataFB, threadID="1234567890", themeName="love")

# Common entry point:
_changeTheme.func(dataFB, action="list")
_changeTheme.func(dataFB, "1234567890", "default")
```

| Function | Vivaran |
|---|---|
| `listThemes(dataFB)` | Themes list lene ke liye GraphQL `MWPThreadThemeQuery_AllThemesQuery` call karna. |
| `findTheme(dataFB, themeName)` | ID, exact naam, ya keyword se match karna. |
| `changeTheme(dataFB, threadID, themeName, initiatorID=None, timeout=20)` | Thread ke liye 4 LS tasks publish karke theme badalna. |
| `func(dataFB, threadID=None, themeName=None, action="set", **kwargs)` | Common entry point: `list` / `find` / `set`. |

**Return:**

- ✅ `{ "success": 1, "messages": "...", "data": { "threadID": ..., "themeID": ..., "themeName": ... } }`
- ❌ `{ "error": 1, "messages": "...", "details"|"payload"|"raw": ... }`

**Mechanism:**

- `listThemes` GraphQL `doc_id=24474714052117636` use karta hai.
- `changeTheme` 4 queues publish karta hai: `ai_generated_theme`,
  `msgr_custom_thread_theme`, `thread_theme_writer`, `thread_theme`.

---

### `_unsend.py`

```python
func(messageID, dataFB)
```

`messageID` se message vapas lena. Endpoint: `/messaging/unsend_message/`.

- ✅ `{ "success": 1, "messages": "Message successfully recalled." }`
- ❌ `Exception({...})` return karta hai.

---

### `_message_requests.py`

```python
func(dataFB)
```

Pending messages ki list lena (`PENDING`).

- ✅ `{ "success": 1, "messageRequests": "<formatted json string>" }`

Content mein senders ki list, snippet, timestamp aur `total_count` hota hai.

---

### `_createNotes.py`

**Messenger Notes** manage karna — Messenger inbox ke upar dikhne wala status-type note,
default 24 ghante rehta hai. Yeh module `ws3-fca/notes.js` (@ChoruOfficial) ka fbchat-v2 style port hai.

```python
from _messaging import _createNotes

_createNotes.checkNote(dataFB)
_createNotes.createNote(dataFB, text, privacy="FRIENDS")
_createNotes.deleteNote(dataFB, noteID)
_createNotes.recreateNote(dataFB, oldNoteID, newText, privacy="FRIENDS")

# Ya unified entry point:
_createNotes.func(dataFB, action="check")
_createNotes.func(dataFB, action="create",   text="Hello", privacy="FRIENDS")
_createNotes.func(dataFB, action="delete",   noteID="<note_id>")
_createNotes.func(dataFB, action="recreate", oldNoteID="<id>", newText="...")
```

| Function | Vivaran |
|---|---|
| `checkNote(dataFB)` | Account ka current note return karna (`msgr_user_rich_status`). |
| `createNote(dataFB, text, privacy="FRIENDS")` | Naya text note banana, duration 86400s (24h). |
| `deleteNote(dataFB, noteID)` | `rich_status_id` se note delete karna. |
| `recreateNote(dataFB, oldNoteID, newText, privacy="FRIENDS")` | Purana note delete karke naya banana (atomic 2-step). |
| `func(dataFB, action, **kwargs)` | Common entry point — `action` ∈ `"check" / "create" / "delete" / "recreate"`. |

**`privacy` Parameter** (case-insensitive):

| Diya gaya value | Map hota hai |
|---|---|
| `"FRIENDS"` *(default)* | `FRIENDS` |
| `"EVERYONE"` · `"PUBLIC"` | `FRIENDS` *(Messenger Notes abhi sirf FRIENDS support karta hai)* |
| Kuch aur | UPPERCASE mein rakha jata hai |

**Return:**

- ✅ `{ "success": 1, "messages": "...", "data": {...} }`
- ❌ `{ "error": 1, "messages": "...", "details"|"raw": ... }`

**Mechanism:**

- Check / create / delete ke liye 3 alag GraphQL `friendly_name` / `doc_id` call karta hai.
- `(connect=10s, read=45s)` **timeout** aur `requests.Timeout` / `requests.RequestException` par max 2 baar **retry** hai.
- `json.loads` se pehle Facebook response ka `for (;;);` prefix strip karta hai.
- `client_mutation_id` random 0–10, `session_id` `_core._utils.generate_client_id()` se generate hota hai.

---

## 🔗 Dependency Diagram

`_messaging` mainly `_core` par depend karta hai:

```text
_core._session.dataGetHome(setCookies)  →  dataFB
_core._utils  →  formAll · mainRequests · gen_threading_id
                 generate_session_id · generate_client_id · json_minimal
                 str_base · get_files_from_paths · Headers · parse_cookie_string
```

**Bahari libraries:** `requests`, `paho-mqtt`.

> `_listening_e2ee.py` **aur** `_send_e2ee.py` ko Go binary `fbchat-bridge-e2ee` bhi chahiye (subprocess, Python dependency nahi). `_send_e2ee.py` `_listening_e2ee.py` se `_BridgeProcess`, `_resolve_binary` aur `parse_cookie_string` reuse karta hai — dono ek hi bridge share kar sakte hain.

---

## 💡 Udaaharan

### Text message bhejna

```python
from _messaging._send import api

sender = api()
print(sender.send(dataFB, "Namaste", "1234567890"))
```

### Image upload karke bhejna

```python
from _messaging._attachments import _uploadAttachment
from _messaging._send import api

uploaded = _uploadAttachment("path/to/image.jpg", dataFB)
sender = api()
print(sender.send(
    dataFB,
    "Yeh rahi aapki image",
    "1234567890",
    typeAttachment="image",
    attachmentID=uploaded["attachmentID"],
))
```

### Message par react karna

```python
from _messaging._reactions import func

resp = func(dataFB, "add", "mid.$abc...", "👍")
print(resp.status_code, resp.text)
```

### Bheja hua message edit karna

```python
from _messaging import _editMessage

print(_editMessage.editMessage(dataFB, "mid.$abc...", "Naya content"))
```

### Thread ka theme / background badalna

```python
from _messaging import _changeTheme

print(_changeTheme.func(dataFB, action="list"))
print(_changeTheme.changeTheme(dataFB, "1234567890", "love"))
```

### Message vapas lena

```python
from _messaging._unsend import func
print(func("mid.$abc...", dataFB))
```

### Pending messages lena

```python
from _messaging._message_requests import func
print(func(dataFB))
```

### Messenger Note banana / delete karna (24h status)

```python
from _messaging import _createNotes

# Current note dekhna
print(_createNotes.checkNote(dataFB))

# Naya note banana (default 24h, privacy FRIENDS)
created = _createNotes.createNote(dataFB, "fbchat-v2 code kar raha hoon ❤️")
note_id = created["data"]["id"]

# Note delete karna
_createNotes.deleteNote(dataFB, note_id)

# Ya purana note ek hi call mein naye se replace karna
_createNotes.recreateNote(dataFB, note_id, "v2.1.3 ho gaya 🎉")
```

### Realtime sunna

```python
import threading
from _messaging._listening import listeningEvent

listener = listeningEvent(dataFB)
listener.get_last_seq_id()
threading.Thread(target=listener.connect_mqtt, daemon=True).start()
```

### E2EE sunna (1-1 messages)

```python
import threading
from _messaging._listening_e2ee import listeningE2EEEvent

listener = listeningE2EEEvent(dataFB)
listener.get_last_seq_id()

@listener.on_message
def handle(evt):
    print(listener.bodyResults)        # _listening.py jaisa schema
    print(listener.e2eeBodyResults)    # chatJid / senderJid

threading.Thread(target=listener.connect_mqtt, daemon=True).start()
```

### E2EE message bhejna (listener ka bridge reuse karo)

```python
import threading
from _messaging._listening_e2ee import listeningE2EEEvent
from _messaging._send_e2ee import api as E2EESender

listener = listeningE2EEEvent(dataFB)
threading.Thread(target=listener.connect_mqtt, daemon=True).start()
# (bhejna se pehle "e2eeConnected" event ka intezaar karo)

sender = E2EESender(listener=listener)

@listener.on_message
def on_msg(evt):
    if evt["type"] == "e2eeMessage" and evt["data"].get("text") == "ping":
        print(sender.reply(evt["data"], "pong"))
        # → {'success': 1, 'payload': {'messageID': '3EB0…', 'timestamp': 1715000000000}}
```

### E2EE message bhejna (standalone — bina listener ke)

```python
from _messaging._send_e2ee import api as E2EESender

with E2EESender(dataFB=dataFB, log_level="warn") as sender:
    sender.send(
        chat_jid    = "100012345678",
        contentSend = "hello E2EE",
    )
    sender.send_to_user("100012345678", "hello proactively")
```

---

## 🛠 Samasya Samadhan

| Samasya | Samadhan |
|---|---|
| Message bhejna fail ho raha hai | Cookie aur `dataFB` valid hai check karo; `threadID`/`userID` verify karo; `typeAttachment` uploaded file se match karo. |
| File upload error | Path exist karta hai aur read permission hai check karo; response metadata check karo (Facebook key badal sakta hai). |
| `_editMessage` / `_changeTheme` publish par timeout | Cookie alive hai check karo, `edge-chat.facebook.com` tak WebSocket network check karo, aur thread mein operation ka haq verify karo. |
| `_send_e2ee.api` returns `{"error": 1, ..., "error-code": "not_connected"}` | Standalone mein `sender.connect()` bhool gaye; reuse mode mein listener ke `connect_mqtt()` ka `e2eeConnected` event aane tak intezaar karo. |
| `_send_e2ee.api` returns `{"error": 1, ..., "error-code": "invalid_chat_jid"}` | Galat destination. Full JID `<facebook_id>@msgr` ya Facebook numeric ID use karo; group `threadID` / username mat use karo. |
| Bridge log `can't encrypt message for device: no signal session established` | Nayi rebuilt binary use karo; bridge ab encrypted DM task automatically chalata hai aur send se pehle `whatsmeow` se prekey fetch karne ke liye missing session report karta hai. Baar baar test karne par `--persist-device --device-path ./e2ee_device.json` add karo Signal session rakhne ke liye. |

---

<div align="right">

⬆️ [Main README par jao](../../README.md) · 🇬🇧 [English](README_EN.md)

</div>
