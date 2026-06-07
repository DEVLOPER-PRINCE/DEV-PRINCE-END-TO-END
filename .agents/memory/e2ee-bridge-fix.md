---
name: E2EE bridge build fix
description: Go build error fix for DeviceStore missing PrivacyTokenStore interface method
---

When building `bridge-e2ee/` with newer whatsmeow, `DeviceStore` must implement `DeleteExpiredPrivacyTokens` with exact signature:

```go
func (ds *DeviceStore) DeleteExpiredPrivacyTokens(ctx context.Context, before time.Time) (int64, error) {
    return 0, nil
}
```

**Why:** whatsmeow updated `store.PrivacyTokenStore` interface — the method now takes a `time.Time` cutoff and returns `(int64, error)`, not just `error`.

**How to apply:** If `go build` fails with "missing method DeleteExpiredPrivacyTokens" or "wrong type", add/fix this stub in `bridge-e2ee/bridge/store.go`.
