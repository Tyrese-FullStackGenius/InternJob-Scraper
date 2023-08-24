#FROM python:3.10-slim
FROM arm64v8/python:3.10

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1


RUN apt-get update \
    # dependencies for building Python packages
    && apt-get install -y build-essential \
    # psycopg2 dependencies
    && apt-get install -y libpq-dev \
    # cleaning up unused files
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

# Copy Code and Install Python pip requirements
COPY ./requirements.txt /requirements.txt
COPY ./requirements-prod.txt /requirements-prod.txt
RUN pip install -r /requirements-prod.txt
COPY . /app

# RUN sed -i 's/\r$//g' /entrypoint is used to process the line endings of the shell scripts,
# which converts Windows line endings to UNIX line endings.

#COPY ./compose/staging/entrypoint.sh /entrypoint
#RUN sed -i 's/\r$//g' /entrypoint
#RUN chmod +x /entrypoint

COPY ./compose/staging/start.sh /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

WORKDIR /app
RUN mkdir /app/logs

EXPOSE 80

#ENTRYPOINT ["/entrypoint"]
CMD ["/start"]
