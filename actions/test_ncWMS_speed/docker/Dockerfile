FROM ubuntu:20.04

MAINTAINER Rod Glover <rglover@uvic.ca>

# Get set to install packages
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update

# Set the locale
RUN apt-get -y install locales && \
    locale-gen en_CA.utf8
ENV LANG en_CA.utf8
ENV LANGUAGE en_CA:en
ENV LC_ALL en_CA.UTF-8

# Install the packages required to install PyCDS.
RUN apt-get install -yq \
            libpq-dev \
            python3 \
            python3-dev \
            python3-pip \
            && \
    pip3 install -U pip pytest

ADD . /app
WORKDIR /app

RUN pip3 install -i https://pypi.pacificclimate.org/simple/ -r requirements.txt
