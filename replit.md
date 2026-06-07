# fbchat-v2 (FBChat-Remake)

An unofficial modern Python library for the Facebook Messenger API. Interacts with Facebook as a real user via cookies — not the Graph API — enabling full Messenger access including End-to-End Encrypted (Secret Conversations) support.

## Tech Stack

- **Python 3.12** — core library
- **Go 1.24+** — E2EE bridge (optional, for Secret Conversations)
- **paho-mqtt** — real-time MQTT listener
- **requests** — HTTP calls to Facebook endpoints

## Architecture

Three-layer design under `src/`:
- `_core/` — session, login, utilities
- `_features/` — Facebook/thread actions
- `_messaging/` — send, receive, react, listen

## Running the Bot

1. Add your Facebook session cookies to `src/config.json`:
   ```json
   {
     "cookies": "c_user=...; xs=...; fr=...; datr=...;",
     "prefix": "/",
     "admins": ["your_facebook_id"]
   }
   ```
2. The workflow `Start application` runs: `PYTHONPATH=src python src/main.py`

## E2EE Bridge (optional)

For Secret Conversations support, build the Go bridge:
```bash
cd bridge-e2ee
git clone https://github.com/mautrix/meta.git ./meta
go mod tidy
go build -ldflags="-s -w" -o ../build/fbchat-bridge-e2ee .
```

## User Preferences

- Keep the three-layer architecture (`_core` → `_features` → `_messaging`) strictly — no reverse imports
- Every public module exposes `func(dataFB, ...)` or a class following the `{"success": 1, ...}` / `{"error": 1, ...}` return shape
- Synchronous only — no async/await
- `PYTHONPATH=src` must be set when running
