FROM nginx:1.21

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d

# Source: https://testdriven.io/blog/dockerizing-django-with-postgres-gunicorn-and-nginx/#nginx