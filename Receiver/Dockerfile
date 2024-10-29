FROM ubuntu:22.04
LABEL maintainer="esotelo2@my.bcit.ca"
RUN apt-get update -y && \
    apt-get install -y python3 python3-pip
# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN python3 -m venv venv 
RUN python3 -m pip install -r requirements.txt 
RUN source venv/bin/activate
COPY . /app
ENTRYPOINT [ "python3" ]
CMD [ "app.py" ]
