# Use an official Python runtime as a parent image
FROM tiangolo/uwsgi-nginx-flask:python3.6

# Set the working directory to /worship-manager
WORKDIR /app

# Copy the current directory contents into the container at /worship-manager
COPY ./app /app/app
COPY ./run.py /app/main.py
COPY ./requirements.txt /app/requirements.txt
COPY ./uwsgi.ini /app/uwsgi.ini


# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Make port 8080 and 8888 available to the world outside this container
EXPOSE 8080
EXPOSE 8888

# Run app.py when the container launches
CMD ["python", "main.py"]
