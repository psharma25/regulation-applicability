# Devcontainer Dockerfile for Codespaces
ARG VARIANT="3.11-bullseye"
FROM mcr.microsoft.com/devcontainers/python:${VARIANT}

# Run as root to install packages
USER root

# Install common system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install python requirements for the test app (if present)
COPY ./test/llm-rag-approval/requirements.txt /tmp/requirements.txt
RUN if [ -f /tmp/requirements.txt ]; then pip install --no-cache-dir -r /tmp/requirements.txt; fi

# Ensure the start script is executable in the container post-create step if available
# (postCreateCommand will run it).

# Switch back to non-root user used by devcontainers
USER vscode
