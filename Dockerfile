FROM python:3.15-slim-bookworm@sha256:122756f3fe72c4f5d3d71897888204ee85774bc79de952555b8a474e1d0a5d53
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libc6-dev make git curl unzip bzip2 ca-certificates \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /workspace
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV OUTPUT_DIR=/output
CMD ["bash", "scripts/build.sh"]
