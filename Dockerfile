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

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 1111
CMD ["python3", "-u", "app.py"]
