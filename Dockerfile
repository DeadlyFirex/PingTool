# Use an official Python runtime as a parent image
FROM python:3.10 AS base
LABEL authors="deadly"

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Make port 8000 available to the world outside this container
EXPOSE 12500

# Run server when the container launches
CMD ["python", "server.py", "--host", "0.0.0.0", "--port", "12500"]