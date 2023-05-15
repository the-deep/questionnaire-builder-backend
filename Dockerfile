FROM python:3.11.3-slim-buster

LABEL maintainer="Deep Dev dev@thedeep.io"

ENV PYTHONUNBUFFERED 1

WORKDIR /code

COPY pyproject.toml poetry.lock /code/

RUN apt-get update -y \
    && apt-get install -y --no-install-recommends \
        # Basic Packages
        iproute2 git vim \
        # Build required packages
        gcc libc-dev libproj-dev \
        # NOTE: procps: For pkill command
        procps \
        # Deep Required Packages
        wait-for-it binutils \
    # Upgrade pip and install python packages for code
    && pip install --upgrade --no-cache-dir pip poetry \
    && poetry --version \
    # Configure to use system instead of virtualenvs
    && poetry config virtualenvs.create false \
    && poetry install --no-root \
    # Clean-up
    && pip uninstall -y poetry virtualenv-clone virtualenv \
    && apt-get remove -y gcc libc-dev libproj-dev \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*


COPY . /code/
