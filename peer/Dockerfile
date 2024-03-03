# Use an official Python runtime as a parent image
FROM python:3.10

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /code

# Copy the current directory contents into the container at /code
COPY . /code/

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Stand in peer directory
WORKDIR /code/peer

# Environment variables
ARG ENV_PCLIENT
ARG ENV_PSERVER

RUN ["python", "pclient.py", "ENV_PCLIENT", "ENV_PSERVER"]