# Use an official Python runtime as a parent image
FROM python:3.8

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install cron
RUN apt-get update && apt-get install -y cron

# Set the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Copy the project code into the container
COPY . /app/

# Command to start services
CMD ["sh", "-c", "service cron start; python manage.py runserver 0.0.0.0:8000"]