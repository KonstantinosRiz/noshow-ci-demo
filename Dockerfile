# Start from a small Linux image that already has Python 3.11
FROM python:3.11-slim

LABEL org.opencontainers.image.source=https://github.com/KonstantinosRiz/noshow-ci-demo

# Work inside /app in the image
WORKDIR /app

# Install libraries first (this layer is cached as long as requirements.txt doesn't change)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Then copy the code and tests
COPY . .

# What runs if you start the container without a command
CMD ["python", "-c", "import noshow; print('noshow image OK')"]
