FROM nginx:alpine

# Remove default nginx config
RUN rm -f /etc/nginx/conf.d/default.conf

# Copy nginx config
COPY deploy/website/nginx.conf /etc/nginx/conf.d/default.conf

# Copy website static files
COPY website/ /usr/share/nginx/html/

# Create ACME challenge directory for Let's Encrypt
RUN mkdir -p /var/www/acme

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
