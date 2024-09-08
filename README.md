# Thailand Driving License Theory Test Simulation (Car & Motorbike)

This app is hosted at: [thaidrivingtest.com](https://thaidrivingtest.com/)

Questions are adapted from the Driving License Requisition Manual issued by the Thailand Department of Land Transport.

The question database contains 150 questions, many with pictures (250 pixel width).

The app simulates the conditions of the real exam: 50 questions in 50 minutes. Each question is multiple choice with 4 options. Pass rate is 90%.

Question wording matches that of the real exam (i.e. occasionally confusing, often non-native sounding English).

The project was put together in PyCharm using Python 3.9 with Flask, and Gunicorn WSGI. The front end makes extensive use of Bootstrap.

#### Technical spec

Start the App for development

```bash
    pip install -e .
    python driving_theory_test
```

Start the App for deployment in prod

```bash
    pip install -U .
    gunicorn 'driving_theory_test:create_app()'
```

#### Screenshots

![qestion](https://github.com/lostintime101/driving_theory_test/assets/92709487/fec45cee-4f96-42dc-b45a-c8b10f2ed365)
