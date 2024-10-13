FROM python:3.13.0-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt ./
RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt

COPY bot/ ./bot

CMD ["python", "bot/main.py"]
