FROM python:3.10

COPY requirements.txt .

RUN pip install -r requirements.txt

VOLUME /eshop

EXPOSE 8000

CMD ["python", "manage.py", "runserver"]