FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip

COPY ./requirements/prod.txt /app/requirements/prod.txt

RUN python -m pip install --no-cache-dir -r /app/requirements/prod.txt

COPY ./ /app

WORKDIR /app
ENV PYTHONPATH=/app

CMD ["uvicorn", "src.main:app", "--proxy-headers", "--forwarded-allow-ips", "*", "--host", "0.0.0.0", "--port", "8000", "--reload"]

HEALTHCHECK --start-period=2s --interval=30s --timeout=5s CMD curl -f http://localhost:/ping | grep pong || exit 1
