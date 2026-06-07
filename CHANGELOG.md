# Changelog

`fbchat-v2` ke sabhi notable changes yahan record kiye jayenge.

Format [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) par based hai,
aur versioning [Semantic Versioning](https://semver.org/) follow karta hai.

---

## [2.1.3b] — 2026-05-18

### 🛠 Changed

- `_messaging/_send_e2ee.py`: Facebook numeric ID se proactive send flow aur
  behtar kiya gaya.
  - `normalize_chat_jid(...)` / `chat_jid_from_user_id(...)` ab bhi normalize
    karta hai `100012345678` → `100012345678@msgr`.
  - `api.send(...)` full JID aur user ID dono accept karta hai; galat input par
    `invalid_chat_jid` zyada clearly return hota hai.
  - `api.send_to_user(...)` proactive flow ke liye convenient entry point hai.
- `src/_e2ee_send_test.py`: test script ab khud `--device-path` ko `fbchat-v2`
  root se relative resolve karta hai, isliye bridge spawn karte waqt cwd par
  depend nahi karta.
- `bridge-e2ee`: proactive E2EE send ke liye root-level fix.
  - `Client.sendE2EEMessage(...)` bhejne se pehle encrypted DM thread ensure
    karta hai.
  - `DeviceStore.GetManySessions()` maange gaye saare session addresses return
    karta hai taaki `whatsmeow` pehchan sake ki device ka session nahi hai aur
    khud prekey fetch kare.
  - `NewDeviceStore(...)` device file ke parent folder ko automatically create
    karta hai agar exist nahi karta, `./src/e2ee_device.json` jaisa path fail
    nahi hoga naye save par.

### 📝 Documentation

- `DOCS.md`, `src/_messaging/README.md`, `src/_messaging/README_EN.md`:
  `can't encrypt message for device: no signal session established` error ke liye
  troubleshooting update aur nayi bridge binary ka istemal.

### ⚠️ 2.1.3 se upgrade karne par dhyan do

- Agar `--persist-device` use karte ho, toh `build/fbchat-bridge-e2ee.exe` par
  latest binary rakho taaki session/prekey fixes kaam karein.
- Python API mein koi breaking change nahi hai.

## [2.1.3] — 2026-05-18

### ✨ Added

- **`src/_e2ee_send_test.py`** — `_messaging/_send_e2ee.py` ke liye alag test
  script.
  - Bina parameter chalane par interactive `receiver UID/JID` aur `bhejne ka
    content` poochha jaega.
  - `--dry-run` Facebook numeric ID → `<id>@msgr` normalize karne ki jaanch
    karta hai bina cookie/bridge ke.
  - Real send mode `FBCHAT_COOKIE` ya `src/config.json` se cookie padhta hai,
    khud `dataGetHome(...)`, bridge connect karta hai aur `send_to_user(...)` /
    `send(...)` call karta hai.
  - `--reply-message`, `--reply-sender-jid`, `--persist-device`,
    `--device-path`, `--binary-path`, connect/send timeout support karta hai.

- **`_messaging/_editMessage.py`** — naaya module jo **bheje hue messages edit**
  karne deta hai MQTT Lightspeed task `queue_name="edit_message"` ko `/ls_req`
  par publish karke.
  - Main API: `editMessage(dataFB, messageID, newText, timeout=20)`.
  - fbchat-v2 style alias: `func(dataFB, messageID, newText, timeout=20)`.
  - Khud `edge-chat.facebook.com` se short-lived MQTT WebSocket connection
    kholat hai, task publish karta hai phir client band karta hai.
  - Return schema:
    - ✅ `{"success": 1, "messages": "...", "data": {"messageID": str, "text": str, ...}}`
    - ❌ `{"error": 1, "messages": "...", "payload": {...}}`
  - Note: success ka matlab hai task successfully publish hua; Messenger phir bhi
    reject kar sakta hai agar message bahut purana ho, current account ka na ho,
    ya edit karne ki permission na ho.

- **`_messaging/_changeTheme.py`** — naaya module **Messenger thread themes ki
  list lene aur theme / background badalne** ke liye.
  - `listThemes(dataFB)` GraphQL `MWPThreadThemeQuery_AllThemesQuery`
    (`doc_id=24474714052117636`) call karta hai.
  - `findTheme(dataFB, themeName)` theme ID, exact name, ya case-insensitive
    keyword se match karta hai.
  - `changeTheme(dataFB, threadID, themeName, initiatorID=None, timeout=20)`
    4 LS queues publish karta hai: `ai_generated_theme`, `msgr_custom_thread_theme`,
    `thread_theme_writer`, `thread_theme`.
  - `func(dataFB, threadID=None, themeName=None, action="set", **kwargs)`
    `action="list"`, `action="find"`, aur default theme set support karta hai.
  - fbchat-v2 ke `success/error` standard ke hisaab se return shape.

### 📝 Documentation

- README VI/EN: feature list, Messaging architecture, file tree, embedded mindmap,
  Quick Start for `_editMessage`, `_changeTheme`, `_createNotes`, aur roadmap
  update kiye gaye.
- `DOCS.md`: **§8 Editing a sent message** aur **§10 Changing a thread theme /
  background** add kiye; baad ke sections §11–§16 ho gaye; edit/theme FAQ add.
- `CLAUDE.md`: file tree, Layer 3 table, dependencies, release/backlog status
  update aur `_editMessage.py` ko E2EE bridge ke JSON-RPC expose na hone wale
  `editMessage` se alag karne ka note.
- `FLOWCHART.md`, `mindmap-mermaid.md`: `_editMessage.py` aur `_changeTheme.py`
  nodes add kiye; MQTT se LS task publish ka runtime flow dikhaya.
- `src/_messaging/README.md` + `README_EN.md`: module reference, examples,
  dependency map aur dono naye modules ke liye troubleshooting.

### 🛠 Changed

- `_messaging/_send_e2ee.py`: Facebook numeric ID se proactive sending support.
  - `normalize_chat_jid(target)` / `chat_jid_from_user_id(user_id)` add kiya
    `100012345678` → `100012345678@msgr` convert karne ke liye.
  - `api.send(...)` ab full JID `<facebook_id>@msgr` aur Facebook numeric ID
    dono accept karta hai; galat input `error-code="invalid_chat_jid"` return
    karta hai.
  - `api.send_to_user(user_id, contentSend, ...)` add kiya jab `chatJid` wala
    event nahi hota toh proactive message bhejne ke liye.
- `bridge-e2ee`: `<facebook_id>@msgr` par proactive E2EE DM bhejne se pehle,
  bridge khud `CreateWhatsAppThreadTask` (`ENCRYPTED_OVER_WA_ONE_TO_ONE`) aur
  server ke return kiye subtasks run karta hai taaki `can't encrypt message for
  device: no signal session established` error na aaye.
- `bridge-e2ee`: `DeviceStore.GetManySessions()` fix kiya taaki existing Signal
  session addresses ke saath missing ones bhi `nil` value se return ho; isse
  `whatsmeow` device ka missing session pehchan kar khud prekey fetch karta hai
  bajay skip karne aur `no signal session established` report karne ke.
- `_messaging/__init__.py`: `__all__` mein `_editMessage`, `_changeTheme` add
  kiye, saath hi `_listening_e2ee` aur `_send_e2ee` public module list mein rakhe.

### 📦 Dependencies

- Koi naya package nahi. Dono naye modules `requests` aur `paho-mqtt` reuse
  karte hain jo `requirements.txt` mein pehle se hain.

### ⚠️ 2.1.2b se upgrade karne par dhyan do

- **Koi breaking change nahi.** Existing modules ke imports/API waise hi hain.
- `_editMessage.py` aur `_changeTheme.py` MQTT LS task use karte hain; active
  cookie chahiye aur network `edge-chat.facebook.com` WebSocket block nahi
  karna chahiye.

---

## [2.1.2b] — 2026-05-15

### ✨ Added

- **`_messaging/_createNotes.py`** — naaya module **Messenger Notes** manage
  karne ke liye (24h status jo Messenger inbox ke upar dikhta hai).
  `ws3-fca/notes.js` (© @ChoruOfficial) se fbchat-v2 style mein port kiya.
  - 4 independent CRUD functions:
    - `checkNote(dataFB)` — current note lo (`msgr_user_rich_status`).
    - `createNote(dataFB, text, privacy="FRIENDS")` — 24h text note banao.
    - `deleteNote(dataFB, noteID)` — `rich_status_id` se note delete karo.
    - `recreateNote(dataFB, oldNoteID, newText, privacy="FRIENDS")` — delete +
      create atomically (koi step fail ho toh fail-fast abort).
  - Unified entry point:
    `func(dataFB, action="check"|"create"|"delete"|"recreate", **kwargs)`.
  - Har call alag GraphQL `friendly_name` / `doc_id` hit karta hai — mutations
    share nahi hote, `delete` mein error `create` par cascade nahi karta:
    - `MWInboxTrayNoteCreationDialogQuery` (doc_id `30899655739648624`)
    - `MWInboxTrayNoteCreationDialogCreationStepContentMutation`
      (doc_id `24060573783603122`)
    - `useMWInboxTrayDeleteNoteMutation` (doc_id `9532619970198958`)
  - **Privacy mapping** (`PRIVACY_ALIASES`): `EVERYONE` / `PUBLIC` dono
    `FRIENDS` pe normalize ho jaate hain (Messenger Notes abhi sirf FRIENDS
    scope support karta hai). Input auto-uppercase, baaki values as-is forward.
  - **Resilience**: `timeout=(connect=10s, read=45s)` + 2 retries for
    `requests.Timeout` / `requests.RequestException` (total ≤ 3 attempts).
  - `json.loads` se pehle `for (;;);` prefix khud strip karta hai.
  - `client_mutation_id` random `0-10`; `session_id` internally
    `generate_client_id()` se — caller ko pass nahi karna padta.
  - **Standard fbchat-v2 return schema**:
    - ✅ `{"success": 1, "messages": "...", "data": {...}}`
    - ❌ `{"error": 1, "messages": "...", "details" | "raw": ...}`
  - Hard-coded `duration = 86400s` (24h) — Messenger web flow abhi arbitrary
    duration support nahi karta.

### 📝 Documentation

- `DOCS.md`: **§10 Messenger Notes (24h status)** add kiya full CRUD examples ke
  saath, function reference table (GraphQL `friendly_name` ke saath), privacy
  mapping table, return shape, internals; **§13 FAQ** mein Messenger Notes
  subsection; §10–§14 renumber.
- `src/_messaging/README.md` + `README_EN.md`: `_createNotes.py` ko file tree,
  table of contents, module reference, dependency map aur usage example block
  mein add kiya.
- `CLAUDE.md`: `_createNotes.py` ko file tree + Layer 3 table mein add kiya.
- `FLOWCHART.md`, `mindmap-mermaid.md`: naaya module reflect karne ke liye
  diagrams update kiye.
- README VI/EN: file tree + Quick Start mein `createNotes` mention update kiya.

### 🛠 Changed

- 6 module files ke tutorial comments mein remaining legacy `__facebookToolsV2`
  references replace kiye (ab standard class name use hota hai).
- `_reactions.py` aur `_get_user_info.py` mein contact link Prince Malhotra ke
  GitHub se update kiya.

### 🔧 Fixed

- `_changeNickname.py` ke tutorial mein typo `datatFB` → `dataFB` fix kiya.

### 📦 Dependencies

- Koi badlaav nahi.

### ⚠️ 2.1.2a se upgrade karne par dhyan do

- **Koi breaking change nahi.** Sirf naaya module `_createNotes` add hua —
  existing code par koi asar nahi.
- Corresponding PyPI release stable tag pe:
  [`fbchat-v2 2.1.4`](https://pypi.org/project/fbchat-v2/2.1.4/).

---

## [2.1.2a] - 2026-05-13

### ✨ Added

- **`_messaging/_send_e2ee.py`** — naaya module `class api` jo **E2EE messages**
  (Secret Conversations) 1-1 conversations mein **bhejna** allow karta hai,
  listener + sender E2EE pair poora karta hai.
  - Do initialization modes:
    - **Reuse** (recommended): `api(listener=listeningE2EEEvent_instance)` —
      listener ke saath Go bridge share karta hai, Meta se dubara pair nahi karta,
      "new device login" notification nahi aati.
    - **Standalone**: `api(dataFB=..., log_level=, device_path=, e2ee_memory_only=, binary_path=)`
      phir `sender.connect()` — alag bridge spawn karta hai. Context manager
      support (`with api(dataFB=...) as sender:`) auto connect/close ke liye.
  - Main API: `send(chat_jid, contentSend, replyMessage="", replySenderJid="")`
    — Go bridge se RPC `sendE2EEMessage` call karta hai.
  - Helper `reply(evt_data, contentSend)` `listeningE2EEEvent` ke event se
    `chatJid` / `id` / `senderJid` khud extract karta hai quick quote-reply ke liye.
  - **Return schema `_send.api.send` se match** — caller code mein branch nahi chahiye:
    - ✅ `{"success": 1, "payload": {"messageID": str, "timestamp": int}}`
    - ❌ `{"error": 1, "payload": {"error-decription": str, "error-code": "bridge_error" | "not_connected"}}`
  - `_BridgeProcess`, `_resolve_binary`, `parse_cookie_string`,
    `_REQUIRED_COOKIES` ko `_listening_e2ee.py` se reuse karta hai — binary
    discovery / cookie parse logic duplicate nahi hoti.

### 📝 Documentation

- `DOCS.md` ko poori tarah English mein rewrite kiya + **FAQ** section add kiya
  ~20 sawaalon ke saath (cookie expiry, `BridgeError`, `chat_jid` vs `threadID`,
  `_send.api` vs `_send_e2ee.api` ka farq, Signal keys persist, etc.).
- `src/_messaging/README.md` + `README_EN.md`: `_send_e2ee.py` ko table of
  contents, module reference, dependency map aur examples (reuse + standalone)
  mein add kiya. Troubleshooting table mein 3 common errors update: `not_connected`,
  `bridge_error`, `ValueError: listener= pass karna zaroori hai`.
- `CLAUDE.md`: `_send_e2ee.py` ko file tree, Layer 3 table aur `_send_e2ee.api`
  ke liye short flow block (mode A vs mode B + return shape) mein add kiya.
- `bridge-e2ee/README.md`: note add kiya ki `sendE2EEMessage` ab Python wrapper
  `_messaging._send_e2ee.api` ke zariye expose hota hai.

### 📦 Dependencies

- Koi badlaav nahi.

---

## [2.1.1] — 2026-05-12

> **Docs & distribution patch.** Runtime mein koi change nahi; mainly website
> docs, README aur PyPI par package push kiya taaki `pip install fbchat-v2`
> officially kaam kare.

### ✨ Added

- **PyPI**: project ab [pypi.org/project/fbchat-v2](https://pypi.org/project/fbchat-v2/) par available hai.
  - `pypi/v` badge (live version) dono `README.md` aur `README_EN.md` ke upar.
  - **📦 PyPI** button dono README ke badge nav bar mein.
  - **PyPI** button (Python icon) website hero (`website/index.html`) mein
    *Source* button ke paas.
- **Website — Naaya E2EE Section** (`#guide-e2ee`):
  - Sidebar Chapter II mein **"E2EE · Encryption"** link add kiya
    (icon `fa-shield-halved`).
  - `_messaging/` file-tree mein `_listening_e2ee.py # E2EE via Go bridge` add.
  - Naaya module card: `_listening_e2ee.listeningE2EEEvent(dataFB)` `@on_message`
    decorator + `send_e2ee_message` sample code ke saath.
  - Architecture, Go bridge build commands, 8 event types table, E2EE send
    example, `device_path` persist, FAQ ke saath bilingual guide page.
- **`CLAUDE.md`** *agent-first* style mein rewrite (Claude / Codex / Copilot):
  TL;DR, "Quick reference" table, *Common gotchas* table (bugs `@attr.s`
  override `__init__`, `EventBuffer` missing method, `BridgeError binary not
  found` listed), Go bridge section clearly separated.

### 🛠 Changed

- **Website home E2EE warning**: `alert--danger` alert *"E2EE NOTICE — bypass
  coming soon"* → `alert--success` **"E2EE READY"** with internal link to
  `#guide-e2ee`.
- README VI/EN: nav bar rearranged so **PyPI** link is right after language links.

### 🔧 Fixed

- Python / Go source code mein koi change nahi.

### 📦 Dependencies

- Koi badlaav nahi.

### ⚠️ 2.1.0 se upgrade karne par dhyan do

- **Koi breaking change nahi.** Upgrade karo:
  ```bash
  pip install --upgrade fbchat-v2
  ```

---

## [2.1.0] — 2026-05-12

> **Bada update:** Messenger direct messages ke liye **End-to-End Encryption
> (E2EE)** decryption officially support ho gaya. Event schema `_listening.py`
> ke saath 100% backward compatible hai — sirf import badlo aur kaam ho jaega.

### ✨ Added

- **`_messaging/_listening_e2ee.py`** — class `listeningE2EEEvent(dataFB)` jo
  decoded 1-1 messages sunti hai, API `listeningEvent` ke compatible:
  - `get_last_seq_id()`, `connect_mqtt()`, `on_message(fn)`, `stop()`.
  - `self.bodyResults` expose karta hai **exact `_listening.py` schema ke saath**
    (`body`, `timestamp`, `userID`, `messageID`, `replyToID`, `type`,
    `attachments.id`, `attachments.url`).
  - `self.e2eeBodyResults` bhi expose karta hai (`chatJid`, `senderJid`) Signal
    Protocol metadata ke liye.
  - `type` = `"user"` / `"thread"` (DM vs group) `chatType` / `isGroup` se
    khud infer karta hai, alag `"e2ee"` value **use nahi karta**.
  - Attachment fallback `"Unable to retrieve attachment ID"` legacy jaisi.
- **`bridge-e2ee/`** — standalone Go bridge (`fbchat-bridge-e2ee[.exe]`) jo
  Python se stdin/stdout par line-delimited JSON-RPC ke zariye baat karta hai.
  Signal Protocol (`whatsmeow`) + Meta Labyrinth (`mautrix-meta`) bundle karta hai.
  - RPC methods: `newClient`, `connect`, `connectE2EE`, `isConnected`,
    `sendMessage`, `sendE2EEMessage`, `disconnect`.
  - Binary path env var `FBCHAT_E2EE_BIN` se override karo.
  - Default `fbchat-v2/build/fbchat-bridge-e2ee[.exe]` se load hota hai.
- **README** (Roman Hindi aur English dono):
  - **System Requirements** section expand: Go 1.24, Git, RAM, Python packages
    list with purpose.
  - **Installation** section 7 steps ke saath, sanity check `python -c "import ..."`
    aur smoke test `python src/main.py`.
  - E2EE bridge build guide detail mein (Go install → `mautrix/meta` clone →
    `go mod tidy` → `go build` → verify).
  - `listeningE2EEEvent` ke liye Quick Start snippet.
- **`src/_messaging/README{,_EN}.md`** — alag **Installation** section (Python
  deps, Go bridge build, `dataFB` contract) aur `_listening_e2ee.py` ke liye
  Module Reference.
- **`CHANGELOG.md`** (yahi file).

### 🛠 Changed

- README: **Important Notice** update kiya "E2EE coming soon" → "E2EE released".
- Mindmap & file tree: `_listening_e2ee.py`, `bridge-e2ee/`, `build/` folder
  add kiya.
- **Roadmap**: E2EE decryption item pe `[x]` tick; naaya item "E2EE bridge as
  prebuilt binary release" add kiya.
- `_messaging/README*.md` troubleshooting table: `FileNotFoundError` (binary
  missing) aur bridge crash ke liye 2 rows add kiye.

### 🔧 Fixed

- `_listening_e2ee.py`: `bodyResults` output ko `_listening.py` se **1-1 match**
  karne ke liye normalize kiya taaki event consuming code mein koi change na
  karni pade.
  - `type` ab `"e2ee"` string nahi hai.
  - `replyToID`, `attachments.id`/`url` legacy ke exact priority order se
    padhte hain (`fbid → id → stickerId`; `url → previewUrl → mercury…preview.uri`).
  - `get_last_seq_id()` sahi format mein log print karta hai (`[<datetime>]last_seq_id: …`)
    aur empty `return` — parity with `_listening.py`.

### 🔒 Security

- Go bridge **alag subprocess** mein chalta hai: bridge crash hone par Python
  crash nahi hota (ctypes/DLL approach se zyada safe).
- `_listening_e2ee` cookie disk par save nahi karta; cookie RPC se memory mein
  pass hoti hai.

### 📦 Dependencies

- **Python**: koi naya package nahi — wahi `requests`, `paho-mqtt`, `attrs`,
  `pyotp`.
- **Go (naaya, optional)**: `mautrix/meta`, `whatsmeow`, `mautrix-go` transitive
  deps. Sirf E2EE bridge build karne ke liye chahiye.

### ⚠️ 2.0.x se upgrade karne par dhyan do

- `_listening.py` use karne wale code mein **koi breaking change nahi**.
- E2EE enable karne ke liye Go 1.24+ install karo aur ek baar binary build karo
  — [README §Installation step 5](README.md#5-optional-build-the-e2ee-bridge--for-1-on-1-messages) dekho.

---

## [2.0.x] — 2024 → 2026-03

- Poore codebase ko 3-layer architecture mein restructure kiya: `_core` /
  `_features` / `_messaging`.
- Group messages ke liye MQTT WebSocket listener (`_listening.py`).
- Full feature set: send / sticker / attachment, react, unsend, message
  requests, group management (admin / nickname / emoji / poll), facebook
  features (post, bio, search, marketplace, professional…).
- Cookie ya username/password (2FA TOTP ke saath) se login.

> 2.0.x versions ki details 12/05/2026 se pehle ke commit history mein hain.

---

[2.1.1]: https://github.com/PrinceMalhotra/fbchat-v2/releases/tag/v2.1.1
[2.1.0]: https://github.com/PrinceMalhotra/fbchat-v2/releases/tag/v2.1.0
[2.0.x]: https://github.com/PrinceMalhotra/fbchat-v2/releases
