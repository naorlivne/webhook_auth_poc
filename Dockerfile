# it's offical so i'm using it + alpine so damn small
FROM python:3.11.3-alpine3.16

# copy the codebase
COPY . /www
RUN chmod +x /www/webhook_auth.py

# install required packages - requires build-base due to gevent GCC complier requirements
RUN apk add --no-cache build-base libffi-dev
RUN pip install -r /www/requirements.txt

# adding the gunicorn config
COPY config/config.py /etc/gunicorn/config.py

#set python to be unbuffered
ENV PYTHONUNBUFFERED=1

#exposing the port
EXPOSE 80

# and running it
CMD ["gunicorn" ,"--config", "/etc/gunicorn/config.py", "webhook_auth:app"]