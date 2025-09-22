FROM nginx:alpine

# Copy the nginx configuration template
COPY nginx-media.conf.template /etc/nginx/templates/default.conf.template

# Expose port 80
EXPOSE 80

# nginx:alpine automatically processes templates in /etc/nginx/templates/
# and substitutes environment variables on startup