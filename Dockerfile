FROM python:3.12-slim

# Prevents Python from buffering logs (helps in CloudWatch).

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first (better caching).

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose port used by uvicorn

EXPOSE 8000

# Start the API

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
 