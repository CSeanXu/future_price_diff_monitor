FROM python:3.7

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.0.5

WORKDIR /opt/
COPY ./ .

RUN pip install -i https://mirrors.aliyun.com/pypi/simple/  "poetry==$POETRY_VERSION" && \
    poetry config virtualenvs.create false                                     &&   \
    poetry install --no-dev --no-interaction --no-ansi

ENTRYPOINT ["python", "main.py"]