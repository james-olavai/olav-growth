#!/bin/sh
set -e

echo "[CDP-INIT] 🛠️ Initializing Marketing Chromium environment..."

# 1. Ensure socat is installed for CDP bridge (Alpine / Ubuntu compatible)
if ! command -v socat >/dev/null 2>&1; then
    echo "[CDP-INIT] Installing socat package..."
    if command -v apk >/dev/null 2>&1; then
        apk add --no-cache socat || true
    elif command -v apt-get >/dev/null 2>&1; then
        apt-get update && apt-get install -y --no-install-recommends socat || true
    fi
fi

# 2. Purge stale singleton locks left by unexpected container restarts
rm -f /config/.config/chromium/Singleton* 2>/dev/null || true
rm -f /config/.config/chromium/Default/Singleton* 2>/dev/null || true

# 3. Ensure labwc autostart exists so Chromium runs with remote debugging port 9223
mkdir -p /config/.config/labwc
if [ ! -f /config/.config/labwc/autostart ]; then
    echo "[CDP-INIT] Creating /config/.config/labwc/autostart..."
    cat <<'EOF' > /config/.config/labwc/autostart
#!/bin/bash
rm -f /config/.config/chromium/Singleton* 2>/dev/null || true
rm -f /config/.config/chromium/Default/Singleton* 2>/dev/null || true

while true; do
    wrapped-chromium \
      --enable-features=UseOzonePlatform \
      --ozone-platform=wayland \
      --remote-debugging-port=9223 \
      --no-first-run \
      --no-default-browser-check \
      ${CHROME_CLI}
    sleep 2
done
EOF
    chmod +x /config/.config/labwc/autostart
fi

echo "[CDP-INIT] ✅ Initialization complete."
