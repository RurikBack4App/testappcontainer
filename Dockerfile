FROM python:3.10.7

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

EXPOSE 8443

CMD ["python", "bot.py"]
