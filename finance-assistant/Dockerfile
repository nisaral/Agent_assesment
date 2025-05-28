FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install uvx

COPY . .

ENV PYTHONPATH=/app
ENV TF_ENABLE_ONEDNN_OPTS=0

EXPOSE 8001 6002 6003 6004 6005 6006 6007