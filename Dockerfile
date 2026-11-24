FROM python:3.15-slim-bookworm@sha256:498829c717b1e59fc42f0e7865eafe4e04ca0f70a3769d4ae70ba218df54507c
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
