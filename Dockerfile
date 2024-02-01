FROM python:3.11-alpine3.17

LABEL authors="ronylitv"

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY ./requirements.txt /app/requirements.txt

# Install any dependencies
RUN pip install --upgrade pip \
    && pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Copy the content of the local src directory to the working directory
COPY . /app


