FROM python:3.11.9

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
ENV DB_PASS ******
ENV DB_HOST 152.32.172.45
ENV DB_PORT 54321

#CELERY
ENV CELERY_BROKER redis://redis:6379/0

# Tasks
ENV DJANGO_SETTINGS_MODULE "core.settings"


COPY requirements.txt .

# install python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

RUN wget https://github.com/TA-Lib/ta-lib/releases/download/v0.4.0/ta-lib-0.4.0-src.tar.gz && \
    tar -xvf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib && \
    ./configure --prefix=/usr --build=`/bin/arch`-unknown-linux-gnu && \
    make && \
    make install && \
    pip install --no-cache-dir TA-Lib

COPY . .

# Manage Assets & DB 
RUN python manage.py collectstatic --no-input
RUN python manage.py makemigrations
RUN python manage.py migrate

# gunicorn
EXPOSE 5005
CMD ["gunicorn", "--config", "gunicorn-cfg.py", "core.wsgi"]