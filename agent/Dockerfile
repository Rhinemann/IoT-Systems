# set base image (host OS)
FROM python:latest
# set the working directory in the container
WORKDIR /usr/agent
# copy the dependencies file to the working directory
COPY agent/requirements.txt .
# install dependencies
RUN pip install --no-cache-dir -r requirements.txt
# copy the content of the local src directory to the working directory
COPY agent/src/ .
# command to run on container start
CMD ["python", "main.py"]