FROM python:3.7-slim
WORKDIR /app
COPY . .
RUN pip3 install -r requirements.txt
CMD gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000 --capture-output --log-level debug