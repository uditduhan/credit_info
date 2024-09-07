FROM python:3.12.5

RUN mkdir /code
WORKDIR /code

RUN apt update && \
    apt install -y postgresql-client

RUN pip install uv

COPY requirements.txt ./
RUN uv pip install --system --no-cache-dir -r requirements.txt

COPY . .