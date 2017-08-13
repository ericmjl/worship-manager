# Use an official Python runtime as a parent image
FROM python:3.6-slim

# Set the working directory to /worship-manager
WORKDIR /worship-manager

# Copy the current directory contents into the container at /worship-manager
COPY . /worship-manager

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 8080

# Run app.py when the container launches
CMD ["python", "app.py"]
