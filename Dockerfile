FROM python:3.11-alpine

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

RUN playwright install webkit

COPY ./ ./

CMD ["python", "main.py", "--headless"]