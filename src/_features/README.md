# `_features` — Feature Layer

> Facebook aur Messenger ke user-level business logic implement karna: profile, posts, search, notifications, Marketplace, thread management…

[![Layer](https://img.shields.io/badge/layer-features-3B82F6)](.)
[![Status](https://img.shields.io/badge/status-stable-22c55e)](.)
[![English](https://img.shields.io/badge/docs-English-blue)](README_EN.md)

---

## 📑 Vishay Suchi

- [Kaam](#-kaam)
- [Directory Structure](#-directory-structure)
- [Public API](#-public-api)
- [`dataFB` Contract](#-datafb-contract)
- [Module Reference](#-module-reference)
  - [`_facebook` — Facebook Business Logic](#facebook--facebook-business-logic)
  - [`_thread` — Thread Management](#thread--thread-management)
- [Dependency Diagram](#-dependency-diagram)
- [Udaaharan](#-udaaharan)
- [Samasya Samadhan](#-samasya-samadhan)

---

## 🎯 Kaam

`_features` session/token **manage nahi karta** (yeh `_core` ka kaam hai). Yeh layer sirf **business logic** par dhyan deti hai:

- 👤 Profile actions: bio, posts, alt profile, professional mode.
- 🔔 User info aur notification lena.
- 🔍 Facebook search · 🚫 block / unblock.
- 🛒 Marketplace listing banana / info lena.
- 👥 Group thread management: naam badalna, emoji, nickname, admin add karna.

---

## 📂 Directory Structure

```text
src/_features/
├── _facebook/                # Facebook account business logic
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
├── README.md                 # ← aap yahan hain
└── README_EN.md
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

`from _features._facebook import *` (ya `_thread`) ke baad aap upar listed modules ko directly call kar sakte hain.

---

## 🧩 `dataFB` Contract

`_features` ke zyaadatar functions **`dataFB`** pehle parameter ke roop mein lete hain — jo `_core._session.dataGetHome(setCookies)` se generate hota hai.

Aam taur par istemal hone wale fields: `fb_dtsg` · `jazoest` · `FacebookID` · `clientRevision` · `sessionID` · `cookieFacebook`.

> 📖 Schema detail: [`_core/README.md`](../_core/README.md#-datafb-contract) dekho.

---

## 📚 Module Reference

### `_facebook` — Facebook Business Logic

#### `_changeBio.py`

```python
func(dataFB, newContents, uploadPost=False)
```

Account bio badalta hai. `uploadPost=True` hone par feed story bhi post hogi.

- ✅ Safal: `{ "success": 1, "messages": ... }`
- ❌ Fail: `{ "error": 1, ... }`

#### `_createPost.py`

```python
func(dataFB, newContents, attachmentID=None)
```

Timeline par naya post banana. `attachmentID` optional parameter hai (abhi current flow mein active nahi hai).

- ✅ `urlPost` return karta hai.
- ❌ API se `error` + message return karta hai.

#### `_professional.py`

```python
func(dataFB, statusBusiness=None)
```

**Professional Mode** on/off karna. `statusBusiness` accept karta hai: `"on"`, `"off"`, `"bat"`, `"band"`, `True`, `False`.

#### `_search.py`

```python
func(dataFB, keywordSearch)
```

Users search karna. Return karta hai:

- `searchResults` — formatted string (bot/CLI ke liye).
- `searchResultsDict` — `{name, id, url}` dicts ki list.

#### `_blocking.py`

```python
func(dataFB, idUser, choiceInteract)
```

User ko block / unblock karna. `choiceInteract`: `"block"` ya `"unblock"`.

#### `_registerOnProfile.py`

```python
func(dataFB, newName, newUsername)
```

Usi account par **alt profile** banana.

> ⚠️ Sirf kuch eligible accounts par kaam karta hai.

#### `_notification.py`

```python
func(dataFB)
```

Notifications ki list lena.

- ✅ `{ "success": 1, "NotificationResults": [...] }`
- ❌ `{ "error": 1, "messages": ... }`

#### `_marketplace.py`

| Function | Maqsad |
|---|---|
| `createItem(dataFB, nameItem, brandItem, priceItem, currencyItem, decriptionItem, hashtagList, typeItem, photoIDList, locationSeller)` | Naya Marketplace product list karna. `photoIDList` `_messaging._attachments` se lena. |
| `getInformationProductItemMarketPlace(dataFB, idProductItem)` | ID ke zariye product details lena. |

#### `_get_user_info.py`

```python
func(dataFB, userID)
```

Chat user info endpoint se user information lena.

- ✅ Detailed info dict.
- ❌ `{ "err": 0 }`.

---

### `_thread` — Thread Management

| Module | Function | Maqsad |
|---|---|---|
| `_changeNameThread.py` | `func(dataFB, threadID, newNameThread)` | Group ka naam badalna. |
| `_changeEmoji.py` | `func(dataFB, threadID, newEmoji)` | Thread ka default emoji badalna. |
| `_addAdmin.py` | `func(dataFB, threadID, idUser, statusChoice=True)` | Admin rights add / remove karna. |
| `_changeNickname.py` | `func(dataFB, threadID, idUser, NewNickname)` | Member ka nickname badalna. |

Sab `_core._utils` se `formatResults("success" \| "error", message)` return karte hain.

#### `_all_thread_data.py`

| Function | Maqsad |
|---|---|
| `func(dataFB)` | INBOX list + `last_seq_id` lena. `dataGet`, `ProcessingTime`, `last_seq_id`, `dataAllThread` return karta hai. |
| `features(dataGet, threadID, commandUse)` | `dataGet` se data nikalna. `commandUse` ∈ `{"getAdmin", "threadInfomation", "exportMemberListToJson"}`. |

---

## 🔗 Dependency Diagram

`_features` mainly `_core` par depend karta hai:

```text
_core._session.dataGetHome(setCookies)  →  dataFB
_core._utils  →  formAll · mainRequests · parse_cookie_string
                 Headers · formatResults · randStr
```

> ⚠️ Facebook ka GraphQL schema ya `doc_id` badlne par toot sakta hai.

---

## 💡 Udaaharan

```python
from _core._session import dataGetHome
from _features._facebook import _notification, _blocking
from _features._thread import _changeEmoji, _all_thread_data

dataFB = dataGetHome("c_user=...; xs=...;")

# Notifications lena
print(_notification.func(dataFB))

# User block karna
print(_blocking.func(dataFB, idUser="1000...", choiceInteract="block"))

# Group emoji badalna
print(_changeEmoji.func(dataFB, threadID="1234567890", newEmoji="🔥"))

# Poora inbox lena
threads = _all_thread_data.func(dataFB)
print(threads["dataAllThread"])
```

---

## 🛠 Samasya Samadhan

| Samasya | Samadhan |
|---|---|
| Bahut saare features mein auth/session error | Cookie expire → nayi `dataFB` banao. |
| API error ya khaali data return kar raha hai | Endpoint / `doc_id` badal gaya; nayi schema ke hisaab se `variables` verify karo. |
| JSON response parse error | Kuch endpoints mein `for (;;);` prefix hota hai — `json.loads` se pehle split karo. |

---

<div align="right">

⬆️ [Main README par jao](../../README.md) · 🇬🇧 [English](README_EN.md)

</div>
