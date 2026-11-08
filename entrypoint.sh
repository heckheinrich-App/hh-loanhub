#!/bin/sh
set -e

# Default PORT to 80 if not injected by Render
export PORT="${PORT:-80}"

# Strip trailing slash from CLOUDFLARE_TUNNEL_URL if present
if [ -n "$CLOUDFLARE_TUNNEL_URL" ]; then
    CLOUDFLARE_TUNNEL_URL=$(echo "$CLOUDFLARE_TUNNEL_URL" | sed 's:/*$::')
    export CLOUDFLARE_TUNNEL_URL
else
    echo "[WARNING] CLOUDFLARE_TUNNEL_URL is not set. API proxying will default to fallback until configured in Render dashboard."
    export CLOUDFLARE_TUNNEL_URL="http://127.0.0.1:8000"
fi

echo "=================================================="
echo " HH LOANHUB - Render Gateway Starting"
echo " Port:           ${PORT}"
echo " Upstream Core:  ${CLOUDFLARE_TUNNEL_URL}"
echo "=================================================="

# Generate actual Nginx configuration
envsubst '${PORT} ${CLOUDFLARE_TUNNEL_URL}' < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf

# Validate Nginx syntax
nginx -t

echo "==> Nginx configuration validated. Launching reverse proxy..."
exec nginx -g "daemon off;"
