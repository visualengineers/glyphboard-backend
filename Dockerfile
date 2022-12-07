FROM python:3.7-slim
COPY . /server
WORKDIR /server
ENV PYTHONUNBUFFERED 1
RUN pip3 install -r requirements.in
EXPOSE 4201
CMD [ "waitress-serve", "--host", "0.0.0.0", "--port", "4201", "server:app" ]