FROM python:3.11.9

# Set the working directory in the container
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# True for development, False for production
ENV DEBUG True
ENV SECRET_KEY <STRONG_KEY_HERE>

# Database settings 这些环境变量在数据库初始化的时候用到
ENV DB_ENGINE timescale.db.backends.postgresql
ENV DB_NAME smart_trader
ENV DB_USERNAME postgres
ENV DB_PASS Spm123!@#
ENV DB_HOST localhost
ENV DB_PORT 5432

#CELERY
ENV CELERY_BROKER redis://redis:6379/0

# Tasks
ENV DJANGO_SETTINGS_MODULE "core.settings"


COPY requirements.txt .

# Install required packages
RUN apt-get update &&  \
    apt-get install -y \
        build-essential \
        wget \
        gcc \
        make && \
    rm -rf /var/lib/apt/lists/*

# Download and install TA-Lib
RUN wget https://github.com/TA-Lib/ta-lib/releases/download/v0.6.4/ta-lib-0.6.4-src.tar.gz && \
    tar -xvf ta-lib-0.6.4-src.tar.gz && \
    cd ta-lib-0.6.4 && \
    ./configure --prefix=/usr && \
    make && \
    make install && \
    cd .. && \
    rm -rf ta-lib-0.6.4 ta-lib-0.6.4-src.tar.gz


# Install the TA-Lib Python package
RUN pip install --no-cache-dir TA-Lib

# install python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


COPY . .

# Manage Assets & DB 
RUN python manage.py collectstatic --no-input
RUN python manage.py makemigrations
RUN python manage.py migrate

# gunicorn
EXPOSE 5005
CMD ["gunicorn", "--config", "gunicorn-cfg.py", "core.asgi:application"]

