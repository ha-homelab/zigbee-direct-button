FROM python:3.15-slim-bookworm@sha256:96599df822d0e1c6bb700014a05c7f3c8cabc6e0f7ff3c4f9f69cee033b4b5d9
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc clang libc6-dev make git curl unzip bzip2 ca-certificates \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /workspace
COPY requirements.lock requirements-build.lock ./
RUN pip install --no-cache-dir --require-hashes --only-binary=:all: -r requirements-build.lock \
    && pip install --no-cache-dir --require-hashes --no-build-isolation \
        --only-binary=:all: --no-binary=PyYAML -r requirements.lock
COPY . .
ENV OUTPUT_DIR=/output
CMD ["bash", "scripts/build.sh"]
