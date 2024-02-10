# Docker-команда FROM вказує базовий образ контейнера
FROM python:3.12

# Install pipenv
RUN pip install pipenv

# Встановимо робочу директорію всередині контейнера
WORKDIR /app

# Copy Pipfile and Pipfile.lock to the container
COPY app/Pipfile app/Pipfile.lock /app/

# Встановимо залежності всередині контейнера
# Install dependencies using pipenv
RUN pipenv install --deploy --system

# Скопіюємо інші файли в робочу директорію контейнера
COPY app /app

ENTRYPOINT ["python3", "__main__.py"]