#!/bin/sh
set -e

# Generates a small runtime config the SPA reads before it boots, so one
# published image can point at a different backend per deployment via a
# plain container env var — no rebuild needed. If API_BASE_URL isn't set,
# emits null and the app falls back to whatever was baked in at build time
# (VITE_API_BASE_URL, already compiled into the JS bundle).
if [ -n "$API_BASE_URL" ]; then
  VALUE="\"$API_BASE_URL\""
else
  VALUE="null"
fi

cat > /usr/share/nginx/html/runtime-config.js <<EOF
window.__RUNTIME_CONFIG__ = {
  API_BASE_URL: ${VALUE}
};
EOF

exec "$@"
