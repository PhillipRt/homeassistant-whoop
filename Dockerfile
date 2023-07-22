# Use the official Python base image
FROM python:3.9

# Install Home Assistant
RUN pip install homeassistant

# Set the working directory
WORKDIR /workspace
