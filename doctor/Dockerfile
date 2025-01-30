FROM python:3.10-slim

RUN apt-get update && apt-get install -y wget netcat-openbsd && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/requirements.txt
COPY .env /app/.env

RUN pip install --no-cache-dir -r requirements.txt
RUN wget https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh -O /usr/local/bin/wait-for-it.sh && \
    chmod +x /usr/local/bin/wait-for-it.sh

COPY . /app

EXPOSE 8003

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8003"]