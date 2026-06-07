# `_features` — Feature Layer

> Implements user-level Facebook & Messenger business logic: profile, posts, search, notifications, Marketplace, thread administration…

[![Layer](https://img.shields.io/badge/layer-features-3B82F6)](.)
[![Status](https://img.shields.io/badge/status-stable-22c55e)](.)
[![Vietnamese](https://img.shields.io/badge/docs-Ti%E1%BA%BFng%20Vi%E1%BB%87t-blue)](README.md)

---

## 📑 Table of Contents

- [Responsibilities](#-responsibilities)
- [Folder Structure](#-folder-structure)
- [Public API](#-public-api)
- [The `dataFB` Contract](#-the-datafb-contract)
- [Module Reference](#-module-reference)
  - [`_facebook` — Facebook actions](#facebook--facebook-actions)
  - [`_thread` — Thread administration](#thread--thread-administration)
- [Dependency Map](#-dependency-map)
- [Examples](#-examples)
- [Troubleshooting](#-troubleshooting)

---

## 🎯 Responsibilities

`_features` does **not** manage session/token concerns (that lives in `_core`). It focuses purely on **business logic**:

- 👤 Profile actions: bio, posts, secondary profile, professional mode.
- 🔔 User info & notification retrieval.
- 🔍 Facebook search · 🚫 block / unblock.
- 🛒 Create / fetch Marketplace listings.
- 👥 Group thread management: rename, emoji, nicknames, admin role.

---

## 📂 Folder Structure

```text
src/_features/
├── _facebook/                # Facebook account actions
│   ├── __init__.py
│   ├── _blocking.py
│   ├── _changeBio.py
│   ├── _createPost.py
│   ├── _get_user_info.py
│   ├── _marketplace.py
│   ├── _notification.py
│   ├── _professional.py
│   ├── _registerOnProfile.py
│   └── _search.py
├── _thread/                  # Group chat management
│   ├── __init__.py
│   ├── _addAdmin.py
│   ├── _all_thread_data.py
│   ├── _changeEmoji.py
│   ├── _changeNameThread.py
│   └── _changeNickname.py
├── README.md
└── README_EN.md              # ← you are here
```

---

## 📦 Public API

```python
# src/_features/_facebook/__init__.py
__all__ = [
    "_changeBio", "_createPost", "_professional", "_search",
    "_blocking", "_registerOnProfile", "_notification",
    "_marketplace", "_get_user_info",
]

# src/_features/_thread/__init__.py
__all__ = [
    "_changeNickname", "_addAdmin", "_changeEmoji", "_changeNameThread",
]
```

After `from _features._facebook import *` (or `_thread`), you can call any module listed above directly.

---

## 🧩 The `dataFB` Contract

Most functions in `_features` accept **`dataFB`** as the first argument — produced by `_core._session.dataGetHome(setCookies)`.

Frequently used keys: `fb_dtsg` · `jazoest` · `FacebookID` · `clientRevision` · `sessionID` · `cookieFacebook`.

> 📖 Full schema: see [`_core/README_EN.md`](../_core/README_EN.md#-the-datafb-contract).

---

## 📚 Module Reference

### `_facebook` — Facebook actions

#### `_changeBio.py`

```python
func(dataFB, newContents, uploadPost=False)
```

Update the account bio. `uploadPost=True` also publishes a feed story.

- ✅ `{ "success": 1, "messages": ... }`
- ❌ `{ "error": 1, ... }`

#### `_createPost.py`

```python
func(dataFB, newContents, attachmentID=None)
```

Create a timeline post. `attachmentID` is reserved (not active in the current flow).

- ✅ returns `urlPost`.
- ❌ returns `error` + API message.

#### `_professional.py`

```python
func(dataFB, statusBusiness=None)
```

Toggle **Professional Mode**. `statusBusiness` accepts: `"on"`, `"off"`, `"bat"`, `"band"`, `True`, `False`.

#### `_search.py`

```python
func(dataFB, keywordSearch)
```

Search users on Facebook. Returns:

- `searchResults` — pre-formatted string (for bots/CLIs).
- `searchResultsDict` — list of `{name, id, url}` dicts.

#### `_blocking.py`

```python
func(dataFB, idUser, choiceInteract)
```

Block / unblock a user. `choiceInteract`: `"block"` or `"unblock"`.

#### `_registerOnProfile.py`

```python
func(dataFB, newName, newUsername)
```

Create an **additional profile** under the same account.

> ⚠️ Only works on eligible accounts.

#### `_notification.py`

```python
func(dataFB)
```

Fetch the notification list.

- ✅ `{ "success": 1, "NotificationResults": [...] }`
- ❌ `{ "error": 1, "messages": ... }`

#### `_marketplace.py`

| Function | Purpose |
|---|---|
| `createItem(dataFB, nameItem, brandItem, priceItem, currencyItem, decriptionItem, hashtagList, typeItem, photoIDList, locationSeller)` | Publish a new Marketplace listing. `photoIDList` comes from `_messaging._attachments`. |
| `getInformationProductItemMarketPlace(dataFB, idProductItem)` | Fetch product details by ID. |

#### `_get_user_info.py`

```python
func(dataFB, userID)
```

Fetch user info via the chat user-info endpoint.

- ✅ Detailed info dictionary.
- ❌ `{ "err": 0 }`.

---

### `_thread` — Thread administration

| Module | Function | Purpose |
|---|---|---|
| `_changeNameThread.py` | `func(dataFB, threadID, newNameThread)` | Rename the group/thread. |
| `_changeEmoji.py` | `func(dataFB, threadID, newEmoji)` | Change the default thread emoji. |
| `_addAdmin.py` | `func(dataFB, threadID, idUser, statusChoice=True)` | Promote / demote admin. |
| `_changeNickname.py` | `func(dataFB, threadID, idUser, NewNickname)` | Change a member's nickname. |

All return `formatResults("success" \| "error", message)` from `_core._utils`.

#### `_all_thread_data.py`

| Function | Purpose |
|---|---|
| `func(dataFB)` | Fetch INBOX list + `last_seq_id`. Returns `dataGet`, `ProcessingTime`, `last_seq_id`, `dataAllThread`. |
| `features(dataGet, threadID, commandUse)` | Drill into `dataGet`. `commandUse` ∈ `{"getAdmin", "threadInfomation", "exportMemberListToJson"}`. |

---

## 🔗 Dependency Map

`_features` mainly depends on `_core`:

```text
_core._session.dataGetHome(setCookies)  →  dataFB
_core._utils  →  formAll · mainRequests · parse_cookie_string
                 Headers · formatResults · randStr
```

> ⚠️ May break when Facebook changes GraphQL schemas or `doc_id`s.

---

## 💡 Examples

```python
from _core._session import dataGetHome
from _features._facebook import _notification, _blocking
from _features._thread import _changeEmoji, _all_thread_data

dataFB = dataGetHome("c_user=...; xs=...;")

# Fetch notifications
print(_notification.func(dataFB))

# Block a user
print(_blocking.func(dataFB, idUser="1000...", choiceInteract="block"))

# Change thread emoji
print(_changeEmoji.func(dataFB, threadID="1234567890", newEmoji="🔥"))

# Fetch the entire inbox
threads = _all_thread_data.func(dataFB)
print(threads["dataAllThread"])
```

---

## 🛠 Troubleshooting

| Symptom | Suggested fix |
|---|---|
| Auth/session errors across multiple features | Cookies expired → regenerate `dataFB`. |
| API returns errors or empty data | Endpoint / `doc_id` changed; verify `variables` against the new schema. |
| JSON parse errors in responses | Some endpoints prefix `for (;;);` — strip it before `json.loads`. |

---

<div align="right">

⬆️ [Back to main README](../../README_EN.md) · 🇮🇳 [Roman Hindi](README.md)

</div>
