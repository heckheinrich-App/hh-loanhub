# HH LOANHUB - Lightweight Cloud Gateway (Render Free Tier)
# Serves static frontend and reverse-proxies /api/* through Cloudflare Tunnel to local Windows PC

FROM nginx:1.27-alpine

# Install gettext for envsubst (already included in nginx:alpine, but ensure dependencies exist)
RUN apk add --no-cache gettext

# Remove default nginx site configuration
RUN rm -rf /etc/nginx/conf.d/* /usr/share/nginx/html/*

# Copy static frontend assets
COPY ui/ /usr/share/nginx/html/

# Copy Nginx template and custom startup script
COPY nginx.conf.template /etc/nginx/templates/default.conf.template
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Render dynamically sets $PORT (defaults to 10000 on free tier)
EXPOSE 80 10000

ENTRYPOINT ["/entrypoint.sh"]
