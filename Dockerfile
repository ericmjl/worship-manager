# Use an official Python runtime as a parent image
FROM python:3.6-slim

# Set the working directory to /worship-manager
WORKDIR /worship-manager

# Copy the current directory contents into the container at /worship-manager
# COPY . /worship-manager
COPY ./static /worship-manager/static
COPY ./templates /worship-manager/templates
COPY ./app /worship-manager/app
COPY ./run.py /worship-manager/run.py
COPY ./requirements.txt /worship-manager/requirements.txt


# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Make port 8080 and 8888 available to the world outside this container
EXPOSE 8080
EXPOSE 8888

# Run app.py when the container launches
CMD ["python", "run.py"]
