FROM python:3.6-slim

# App folders
RUN mkdir /app /app/vendor /app/src
WORKDIR /app/src

COPY requirements.txt /app/src
RUN pip install -r requirements.txt

COPY . ./

CMD python app.py

EXPOSE 5001
