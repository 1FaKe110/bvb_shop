FROM python:3.10.7-slim-bullseye

WORKDIR /usr/src/app

COPY ./src ./

ENV PYTHONUNBUFFERED=1

ENV db_host=46.19.65.251
ENV db_port=5432
ENV db_name=bvb_shop
ENV db_username=gen_user
ENV db_password=bvb_admin

ENV secret_key='eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9'

ENV BOT_TOKEN = '6542986021:AAGhL8Yf4bTLdI5cf48Pf6ryksmaFJW6-7c'
ENV CHANNEL_ID = '-1001845833328'

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 1111
CMD ["python3", "-u", "app.py"]