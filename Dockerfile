FROM python:3.10-bookworm

RUN mkdir -p /app

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY download_models.py .

RUN python download_models.py

COPY . .

EXPOSE 8080

CMD ["python", "app/app.py"]