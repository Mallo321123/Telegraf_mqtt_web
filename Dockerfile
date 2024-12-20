FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
COPY app.py /app/app.py
COPY config.py /app/config.py
COPY templates /app/templates
COPY static /app/static

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python", "app.py"]