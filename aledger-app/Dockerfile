FROM python:3.10
WORKDIR /code
COPY ./requirements/requirements.base.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./aledger /code/aledger
CMD ["uvicorn", "aledger.controllers.http:app", "--host", "0.0.0.0", "--port", "80"]
