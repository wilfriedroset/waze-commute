FROM python:3-alpine

RUN mkdir /app

COPY waze-commute.py /app/waze-commute.py
COPY requirements.txt /app/requirements.txt

RUN pip install -q --no-cache-dir --no-warn-script-location -r /app/requirements.txt \
 && rm -f /tmp/requirements.tx

ENTRYPOINT ["/usr/local/bin/python", "/app/waze-commute.py"]
