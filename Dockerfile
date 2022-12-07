FROM python:3
WORKDIR /app
COPY . .
ENV PYTHONUNBUFFERED 1
RUN pip3 install -r requirements.in
EXPOSE 4201
CMD [ "waitress-serve", "--host", "0.0.0.0", "--port", "4201", "server:app" ]