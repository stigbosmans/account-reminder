FROM python:3.10
WORKDIR /app
COPY ./src /app
COPY requirements.txt /app/requirements.txt
RUN ls
RUN pip install -r ./requirements.txt
CMD ["python", "main.py"]