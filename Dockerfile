FROM python:3

WORKDIR /app
COPY ./requirements.txt /app
RUN pip install --trusted-host pypi.python.org -r requirements.txt
COPY ./app.py /app
CMD ["python", "app.py"]