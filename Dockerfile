FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Installa ngrok per Raspberry Pi (ARM)
RUN apt-get update && apt-get install -y wget unzip && \
    wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-arm64.zip && \
    unzip ngrok-stable-linux-arm64.zip && \
    mv ngrok /usr/local/bin/ && \
    rm ngrok-stable-linux-arm64.zip && \
    apt-get remove -y wget unzip && apt-get autoremove -y

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p logs data

CMD ["python", "-m", "app.main"]    