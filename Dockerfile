FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

ENV FLASK_APP=main.py

ENTRYPOINT ["./entrypoint.sh"]

CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:5000", "--workers", "2"]
