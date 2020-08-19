FROM python:3.7
RUN apt-get update && apt-get install -y \
    curl apt-utils apt-transport-https debconf-utils gcc build-essential
COPY . /app
WORKDIR /app
RUN pip install -e .
EXPOSE 5000
CMD python ./pryno/forever.py pryno/main.py