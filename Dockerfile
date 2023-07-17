# Use an official Python runtime as the base image
FROM python:3.9-slim

SHELL [ "/bin/bash", "-c" ]

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /projects/Adest

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    postgresql-client

# Install Python dependencies
RUN python -m pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the Django project files to the container
COPY . /projects/Adest

# Run database migrations and collect static files
WORKDIR /projects/Adest

# RUN python manage.py migrate
# RUN python manage.py migrate

# RUN python manage.py collectstatic --no-input

# Expose the Django development server port
EXPOSE 8000

# Run the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
