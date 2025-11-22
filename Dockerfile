FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY desktop_app/ ./desktop_app/
COPY .env .

# Set working directory to desktop_app where app.py resides
WORKDIR /app/desktop_app

EXPOSE 5000

CMD ["python", "app.py"]
