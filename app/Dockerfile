# syntax=docker/dockerfile:1.4
FROM python:3.11-alpine

WORKDIR /src
COPY requirements.txt /src
COPY srv.py /src
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

ENV FLASK_APP srv.py
ENV FLASK_RUN_PORT 6000
ENV FLASK_RUN_HOST 0.0.0.0

EXPOSE 6000

# run with python
CMD ["flask", "run"]