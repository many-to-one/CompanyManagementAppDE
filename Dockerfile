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
    postgresql-client \
    -y locales

# Generate the 'pl_PL.UTF-8' locale
RUN echo "pl_PL.UTF-8 UTF-8" >> /etc/locale.gen && \
    locale-gen pl_PL.UTF-8

# Set the locale environment variable
ENV LC_ALL=pl_PL.UTF-8
ENV LANG=pl_PL.UTF-8
ENV LANGUAGE=pl_PL.UTF-8


# Install Python dependencies
RUN python -m pip install --upgrade pip
COPY requirements.txt .
# COPY . /requirements.txt/usr/src/requirements.txt
RUN pip install -r requirements.txt

# COPY entrypoint.dev.sh .
# Set executable permissions for the entrypoint script
# RUN chmod +x entrypoint.dev.sh 

# for windows
# COPY entrypoint.dev.ps1 . 


# Copy the Django project files to the container
COPY . /projects/Adest

# Run database migrations and collect static files
# WORKDIR /projects/Adest

# RUN python manage.py migrate
RUN python manage.py collectstatic --noinput

# ENTRYPOINT ["/projects/Adest/entrypoint.dev.ps1"]

# Set the environment variable for Celery broker URL
# ENV CELERY_BROKER_URL ${CELERY_BROKER_URL}
# ENV GUNICORN_ERROR_LOGFILE ${GUNICORN_ERROR_LOGFILE}

# Expose the Django development server port
# EXPOSE 8000

# Run the Django development server
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
# CMD gunicorn Adest.wsgi:application --bind 0.0.0.0:8000 --workers 5 --error-logfile ${GUNICORN_ERROR_LOGFILE}
# supervisord -n -c /Adest/supervisor.conf
