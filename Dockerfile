FROM python:3.9

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["uvicorn", "app:start", "--host", "0.0.0.0", "--port", "5000"]