#
# Docker file for MessageInABottle S<ID> v1.0
#
FROM python:3.8
LABEL maintainer="MessageInABottle Squad 6 API Gateway"
LABEL version="1.0"
LABEL description="MessageInABottle Application Squad 6"

# setting the workdir
WORKDIR /app

# copying requirements
COPY ./requirements.txt /app
COPY ./requirements.dev.txt /app
COPY ./requirements.prod.txt /app

# installing all requirements
RUN ["pip", "install", "-r", "requirements.prod.txt"]

# creating the environment
COPY . /app

# moving the static contents
RUN ["mv", "/app/mib/static", "/static"]

# exposing the port
EXPOSE 5000/tcp

# Main command
CMD ["gunicorn", "--config", "gunicorn.conf.py", "wsgi:app"]
