FROM python:3.11

COPY requirements.txt /bot/

WORKDIR /bot
RUN pip install -r requirements.txt

COPY . .
CMD ["python3", "bot/main.py"]