FROM python:3.11-slim

WORKDIR /app

COPY . /app

RUN pip install -U .

CMD ["gunicorn", "driving_theory_test:create_app()", "-b", "0.0.0.0:8000"]
