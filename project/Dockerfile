FROM python:3.9

RUN pip install --upgrade pip \
    && mkdir /app

ADD . /app

WORKDIR /app

RUN pip install -r requirements.txt

CMD python /app/nos_ayudamos_bot.py