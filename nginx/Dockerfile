FROM nginx:1.27-alpine

# Remove default configs
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom configurations
COPY nginx.conf /etc/nginx/nginx.conf
COPY http.d/*.conf /etc/nginx/http.d/
COPY stream.d/*.conf /etc/nginx/stream.d/

# Create directory for personal content
RUN mkdir -p /var/www/personal

# Copy blog content
COPY blog_site/ /var/www/personal/

# Create directory and copy HTML content for timeout
RUN mkdir -p /var/www/html
COPY html_timeout/ /var/www/html/