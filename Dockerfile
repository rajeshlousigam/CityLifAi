FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY src/ /app/src

ENV PYTHONUNBUFFERED=1

CMD ["python", "src/__main__.py", "--host", "0.0.0.0", "--port", "8000"]