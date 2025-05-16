FROM rasa/rasa:3.6.21

COPY . /app

RUN ls -la /app

WORKDIR /app

CMD ["run", "--debug", "-m", "/app/models", "--credentials", "/app/credentials.yml", "--endpoints", "/app/endpoints.yml"]
