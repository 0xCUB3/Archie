FROM python:3.11

COPY requirements.txt /app/

WORKDIR /app
RUN pip install -r requirements.txt

COPY . .
CMD ["python3", "main.py"]