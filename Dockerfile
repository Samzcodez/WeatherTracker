# Pull the Python base image
FROM python:3.10-slim-bullseye 

# Set environment variables
ENV APP_PATH=/usr/app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR $APP_PATH

# Install dependencies
RUN apt-get update \
    && apt-get -y install gcc make

# Copy only the poetry files for installing dependencies
COPY pyproject.toml poetry.lock ./

RUN true \
    && pip install poetry \
    && poetry install --without dev --no-ansi \
    && true

# Copy the project files to the working directory
COPY . $APP_PATH

# Expose the Django application server port
EXPOSE 8000

# Set up the entrypoint
COPY entrypoint.sh $APP_PATH/entrypoint.sh
RUN chmod +x $APP_PATH/entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]