## 🎉 fbchat-v2 ab PyPI par available hai!

> **Documentation & distribution infrastructure patch.** Koi runtime change nahi — koi breaking change nahi.
> Is version se aap directly install kar sakte hain:
>
> ```bash
> pip install fbchat-v2
> # ya upgrade karo
> pip install --upgrade fbchat-v2
> ```
>
> 🔗 https://pypi.org/project/fbchat-v2/

---

### ✨ Added

- 📦 **PyPI publish** — `fbchat-v2` package officially Python Package Index par aa gaya.
- 🏷 **`pypi/v` badge (live version)** `README.md` aur `README_EN.md` dono ke top par,
  saath mein nav strip aur website hero mein **PyPI** button.
- 🔐 **Website par naaya E2EE section** (`#guide-e2ee`):
  - Sidebar link **"E2EE · Secret Conversations"** (Chapter II).
  - `_messaging/` file-tree mein `_listening_e2ee.py` add kiya.
  - `listeningE2EEEvent(dataFB)` module card with `@on_message` code example
    + `send_e2ee_message`.
  - Roman Hindi/English bilingual guide: architecture, Go bridge build commands,
    8 event types table, `device_path` persist karna, FAQ.
- 🤖 **`CLAUDE.md` rewrite *agent-first* style mein** (Claude / Codex /
  Copilot): file ke shuru mein TL;DR, *Quick reference* table, *Common gotchas* table
  (`@attr.s` override `__init__`, `EventBuffer` missing method, `BridgeError binary not found`…),
  Go bridge section alag clearly.

### 🛠 Changed

- 🟢 Home website par E2EE warning `alert--danger` ("bypass release hone wali hai") se
  `alert--success` **"E2EE READY"** mein badla with internal link `#guide-e2ee` par.
- 📑 Dono README nav strip reorganize kiya: **PyPI** link bilingual link ke bilkul baad.

### 🔧 Fixed

- _Koi Python / Go source code change nahi._

### 📦 Dependencies

- _Koi change nahi._

---

### ⚠️ 2.1.0 se upgrade note

Koi breaking change nahi. Bas yeh chalao:

```bash
pip install --upgrade fbchat-v2
```

E2EE users (`_listening_e2ee.py`) ko abhi bhi v2.1.0 jaisa Go bridge ek baar build karna padega —
[README §Installation step 5](../README.md) dekho.

---

### 🔗 Links

- 📦 **PyPI**: https://pypi.org/project/fbchat-v2/
- 📖 **Docs**: [DOCS.md](../DOCS.md)
- 📊 **Flowchart**: [FLOWCHART.md](../FLOWCHART.md)
- 📋 **Changelog**: [CHANGELOG.md](../CHANGELOG.md)
- 🐛 **Bug Reports**: https://github.com/PrinceMalhotra/fbchat-v2/issues
- 💬 **Telegram**: https://t.me/PrinceMalhotra

**Full Changelog**: https://github.com/PrinceMalhotra/fbchat-v2/compare/v2.1.0...v2.1.1
