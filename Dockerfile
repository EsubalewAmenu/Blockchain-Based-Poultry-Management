FROM postgis/postgis

FROM python:3.10

ENV PYTHONUNBUFFERED 1

# switch to the app directory so that everything runs from here
WORKDIR /app 

# setup postgis and GDAL
RUN apt-get update &&\
    apt-get install -y binutils libproj-dev gdal-bin libgdal-dev python3-gdal postgis wkhtmltopdf ffmpeg

COPY requirements-local.txt /app/requirements.txt

# installs the requirements
RUN pip install -r requirements.txt

COPY . /app
