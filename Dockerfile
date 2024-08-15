FROM python:3.10.4

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .

# install python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Manage Assets & DB 
RUN python manage.py collectstatic --no-input 
RUN python manage.py makemigrations
RUN python manage.py migrate

# gunicorn
EXPOSE 5005
CMD ["gunicorn", "--config", "gunicorn-cfg.py", "core.wsgi"]
