FROM rasa/rasa:3.6.21

COPY . /app

# Instala canal de Telegram
USER root
RUN pip install rasa[telegram] && \
    pip install -U aiogram==2.25.2
USER 1001

RUN ls -la /app

WORKDIR /app

CMD ["run", "--debug", "-m", "/app/models", "--credentials", "/app/credentials.yml", "--endpoints", "/app/endpoints.yml"]

