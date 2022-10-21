FROM python:slim-buster

# Copying requirements of a project
COPY pyproject.toml setup.py app.py /app/src/
WORKDIR /app/src

# Copying actual application
COPY ./egame179_frontend /app/src/
RUN pip install --no-cache-dir --upgrade .

CMD ["streamlit", "run", "egame179_frontend/app.py" "--logger.level=info",  "2> streamlit.log"]
