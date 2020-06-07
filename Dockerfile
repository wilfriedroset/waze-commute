FROM telegraf:1.14.3

ENV PYTHONIOENCODING=utf-8
COPY waze-commute.py /app/waze-commute.py
COPY requirements.txt /app/requirements.txt

RUN apt update && apt install -qy --no-install-recommends \
      python3 \
      python3-pip \
      python3-setuptools \
      python3-wheel && \
   pip3 install -qr /app/requirements.txt && \
   rm -rf /var/lib/apt/lists/* /app/requirements.txt

EXPOSE 8092/udp 8094 8125/udp
ENTRYPOINT ["/entrypoint.sh"]
CMD ["telegraf"]
