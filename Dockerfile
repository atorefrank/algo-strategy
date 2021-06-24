# Dockerfile

# The first instruction is what image we want to base our container on
# We Use an official Python runtime as a parent image
FROM python:3.8

WORKDIR /code

# Allows docker to cache installed dependencies between builds
COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

# Mounts the application code to the image
COPY src/ .

EXPOSE 8000

# runs the production server
CMD ["python", "./technical_analysis.py"]
# CMD ["runserver", "0.0.0.0:8000"]