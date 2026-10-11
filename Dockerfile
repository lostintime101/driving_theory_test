FROM python:3.14-slim

WORKDIR /app

COPY . /app

RUN pip install -U .

# suppressing the control-socket server that gunicorn 26 starts by default
CMD ["gunicorn", "driving_theory_test:create_app()", "-b", "0.0.0.0:8000", "--no-control-socket"]
