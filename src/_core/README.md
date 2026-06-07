# `_core` — Buniyadi Layer

> `fbchat-v2` ki foundation layer. Session shuru karna, payload banana, cookie parse karna, ID generate karna — upar ki har layer is module par depend karti hai.

[![Layer](https://img.shields.io/badge/layer-core-6E40C9)](.)
[![Status](https://img.shields.io/badge/status-stable-22c55e)](.)
[![English](https://img.shields.io/badge/docs-English-blue)](README_EN.md)

---

## 📑 Vishay Suchi

- [Kaam](#-kaam)
- [Directory Structure](#-directory-structure)
- [Public API](#-public-api)
- [`dataFB` Contract](#-datafb-contract)
- [Module Reference](#-module-reference)
  - [`_session.py`](#sessionpy)
  - [`_utils.py`](#utilspy)
  - [`_facebookLogin.py`](#facebookloginpy)
- [Dependency Diagram](#-dependency-diagram)
- [Udaaharan](#-udaaharan)
- [Samasya Samadhan](#-samasya-samadhan)

---

## 🎯 Kaam

`_core` ek shared technical layer hai — ismein **koi bhi** end-user feature nahi hai. Iski zimmedari:

- 🔑 User cookie se **session** shuru karna.
- 🧱 Facebook endpoints ke liye standard **payload / request** banana.
- 🍪 Cookie parse karna aur **dynamic tokens** nikalana (`fb_dtsg`, `jazoest`, …).
- 🆔 Message bhejne / paane ke liye **ID** generate karna.
- 🛠 `_features` aur `_messaging` ke liye reusable **utilities** dena.

---

## 📂 Directory Structure

```text
src/_core/
├── __init__.py
├── _session.py           # Cookie se dataFB initialize karo
├── _utils.py             # HTTP helpers, parser, ID generator…
├── _facebookLogin.py     # Username/password login (+ 2FA)
├── README.md             # ← aap yahan hain
└── README_EN.md
```

---

## 📦 Public API

```python
# src/_core/__init__.py
__all__ = ["_session", "_utils", "_facebookLogin"]
```

`import _core` ke baad aap `_core._session`, `_core._utils`, `_core._facebookLogin` ke zariye saare sub-modules access kar sakte hain.

---

## 🧩 `dataFB` Contract

`_session.dataGetHome(setCookies)` ek `dict` return karta hai (aam tor par **`dataFB`** naam dete hain) — yeh aage ke har request ka **single source of truth** hai.

| Key | Vivaran |
|---|---|
| `fb_dtsg` | Runtime CSRF token |
| `fb_dtsg_ag` | Kuch endpoints ke liye `fb_dtsg` ka variant |
| `jazoest` | `fb_dtsg` ke saath token |
| `hash` | Current session hash |
| `sessionID` | Runtime session ID |
| `FacebookID` | Login user ka UID |
| `clientRevision` | Client revision (Facebook ke hisaab se update hota hai) |
| `cookieFacebook` | Original cookie dict, `requests` ke liye ready |

> ⚠️ `_features/*` aur `_messaging/*` ke **lagbhag har** module in values par depend karte hain.

---

## 📚 Module Reference

### `_session.py`

#### `dataGetHome(setCookies: str) -> dict`

Diye hue cookie se `https://www.facebook.com/` access karta hai, zaroori tokens nikalata hai.

| Parameter | Type | Vivaran |
|---|---|---|
| `setCookies` | `str` | Raw cookie, jaise `"c_user=...; xs=...; fr=...; datr=...;"` |

**Return:** Upar ke `dataFB` schema ke hisaab se `dict`.

**Process:**

1. Browser-style GET header banana.
2. Cookie string ko dict mein convert karna (`_utils.parse_cookie_string`).
3. Homepage HTML load karna.
4. `_utils.dataSplit` se tokens kaat-na.
5. Session dict return karna.

> ⚠️ Abhi split-marker se nikala jata hai; Facebook ka HTML badlne par toot sakta hai. Account par **checkpoint** bhi aa sakta hai.

---

### `_utils.py`

`_core` ka sabse important module. 5 main function groups hain:

#### A. HTTP / Request

| Function | Vivaran |
|---|---|
| `Headers(dataForm=None, Host=None)` | Standard header set banana; `dataForm` hone par `Content-Length` apne aap add karta hai. |
| `parse_cookie_string(cookie_string)` | Cookie string → `requests` ke liye `dict`. |
| `mainRequests(urlRequests, dataForm, setCookies)` | `requests.post(**kwargs)` ke liye ready `kwargs` return karta hai. |

#### B. Parse / Format

| Function | Vivaran |
|---|---|
| `digitToChar(digit)` | Digit → char convert karna. |
| `str_base(number, base)` | Base badalna. |
| `dataSplit(...)` | Delimiter se string kaat-na. |
| `clearHTML(text)` | Regex se HTML tags hatana. |
| `formatResults(type, text)` | Output `{ "status": ..., "message": ... }` normalize karna. |

#### C. General Form Builder

```python
formAll(dataFB, FBApiReqFriendlyName=None, docID=None, requireGraphql=None)
```

Zyaadatar request flows ka backbone, 2 modes support karta hai:

1. **GraphQL** (`requireGraphql is None`): `fb_api_req_friendly_name`, `doc_id`, `fb_api_caller_class`, … ke saath.
2. **Legacy / minimal** (`requireGraphql != None`): sirf minimum fields.

#### D. Messaging ID Generators

`generate_session_id()` · `generate_client_id()` · `gen_threading_id()` · `json_minimal(data)` · `_set_chat_on(value)`

> `_messaging._send` aur `_messaging._listening` mein zyaada istemal hota hai.

#### E. Aur Utilities

`require_list(list_)` · `get_files_from_paths(filenames)` · `randStr(length)`

---

### `_facebookLogin.py`

Facebook mein **username / password** se login karna (+ optional 2FA).

#### Public Components

| Symbol | Vivaran |
|---|---|
| `class loginFacebook(username, password, AuthenticationGoogleCode=None)` | Login; chalane ke liye `.main()` call karo. |
| `GetToken2FA(key2Fa)` | `https://2fa.live/tok/...` se 2FA OTP lena. |
| `jsonResults(...)` | Return structure normalize karna. |

#### Result

| Status | Return Fields |
|---|---|
| ✅ Safal | `success.setCookies` · `success.accessTokenFB` · `success.cookiesKey-ValueList` |
| ❌ Fail | `error.title` · `error.description` · `error.error_subcode` · `error.error_code` · `error.fbtrace_id` |

> 🔒 Yeh module bahut sensitive data handle karta hai. Production mein **zaroori** cookie-login ka istemal karo.

---

## 🔗 Dependency Diagram

`_core._utils` ko badi jagah import kiya jata hai:

- `src/_features/_facebook/*`
- `src/_features/_thread/*`
- `src/_messaging/*`

Sabse zyaada istemal hone wale helpers:

```text
formAll · mainRequests · parse_cookie_string · Headers · formatResults
gen_threading_id · generate_session_id · generate_client_id
str_base · randStr · get_files_from_paths
```

> ⚠️ **Chetavani:** Core payload / cookie logic badlne par zyaadatar features par chain effect padega.

---

## 💡 Udaaharan

### Cookie se `dataFB` initialize karo

```python
from _core._session import dataGetHome

setCookies = "c_user=...; xs=...; fr=...; datr=...;"
dataFB = dataGetHome(setCookies)

print(dataFB["FacebookID"])
print(dataFB["fb_dtsg"])
```

### GraphQL Request bhejna

```python
import json, requests
from _core._utils import formAll, mainRequests

dataForm = formAll(
    dataFB,
    FBApiReqFriendlyName="CometNotificationsDropdownQuery",
    docID=6770067089747450,
)
dataForm["variables"] = json.dumps({
    "count": 10,
    "environment": "MAIN_SURFACE",
    "scale": 1,
})

resp = requests.post(**mainRequests(
    "https://www.facebook.com/api/graphql/",
    dataForm,
    dataFB["cookieFacebook"],
))
print(resp.status_code)
```

### Minimal Payload (non-GraphQL)

```python
from _core._utils import formAll

payload = formAll(dataFB, requireGraphql=False)
payload["message_id"] = "mid...."
```

---

## 🛠 Samasya Samadhan

| Samasya | Samadhan |
|---|---|
| Bahut saari requests auth/session error de rahi hain | Cookie expire ho gayi → `dataGetHome(...)` se nayi `dataFB` banao. |
| Return fields mein fallback values aa rahe hain | Homepage HTML badal gaya → `_session.py` mein split markers update karo. |
| Login par checkpoint aa raha hai | Cookie-login use karo; agar login flow rakho to IP / 2FA check karo. |

---

<div align="right">

⬆️ [Main README par jao](../../README.md) · 🇬🇧 [English](README_EN.md)

</div>
