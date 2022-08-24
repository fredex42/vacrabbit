FROM python:3.9-alpine

COPY requirements.txt /tmp
RUN pip3 install -r /tmp/requirements.txt
COPY --chmod=755 vacrabbit.py /usr/local/bin
COPY --chmod=755 pushback.py /usr/local/bin
