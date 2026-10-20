FROM python:3.15-slim-bookworm@sha256:2a41267d9de9d358f77a1de356e0f16ecba8d39827855be0ce9ef4792edce402
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc clang libc6-dev make git curl unzip bzip2 ca-certificates \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /workspace
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV OUTPUT_DIR=/output
CMD ["bash", "scripts/build.sh"]
