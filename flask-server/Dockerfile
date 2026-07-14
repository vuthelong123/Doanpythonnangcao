FROM python:3.11-slim

WORKDIR /app

COPY flask-server/requirements.txt ./flask-server/
RUN pip install --no-cache-dir -r flask-server/requirements.txt

COPY . .

EXPOSE 3000

WORKDIR /app/flask-server

CMD ["python", "app.py"]
