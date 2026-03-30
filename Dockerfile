FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# Initialize DB before starting app
CMD ["sh", "-c", "python init_db.py && python app.py"]