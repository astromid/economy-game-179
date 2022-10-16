FROM python:slim-buster

RUN apt-get update && apt-get install -y default-libmysqlclient-dev

# Copying requirements of a project
COPY pyproject.toml setup.py /app/src/
WORKDIR /app/src

# Copying database migrations
COPY alembic /app/src/
COPY alembic.ini /app/src/
# Copying actual application
COPY egame179_backend /app/src/
RUN pip install --no-cache-dir --upgrade .

CMD ["/usr/local/bin/python", "-m", "egame179_backend"]
