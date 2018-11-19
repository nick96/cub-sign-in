from nginx:1.15.6

RUN apt -get install python-certbox-nginx

RUN rm -f /etc/nginx/nginx.conf
COPY nginx.conf /etc/nginx/

RUN rm -f /etc/nginx/conf.d/default.conf
COPY project.conf /etc/nginx/conf.d/

RUN sudo certbox --nginx -d nspain.me -d www.nspain.me
