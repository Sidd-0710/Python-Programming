FROM python:3.13-slim

WORKDIR /srv

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

ENV ENVIRONMENT=production
EXPOSE 8000

# SECRET_KEY and DATABASE_URL are passed in when the container starts, never
# baked into the image:  docker run -e SECRET_KEY=... -e DATABASE_URL=... -p 8000:8000 task-tracker
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
