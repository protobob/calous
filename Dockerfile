FROM python:3.11-slim

WORKDIR /app

# Install only the non-standard dependencies
RUN pip install --no-cache-dir \
    ollama>=0.5.2 \
    rich \
    pydantic \
    asteval

# Create the hiollama directory for data persistence
RUN mkdir -p /root/hiollama

# Set up volume mount point
VOLUME ["/root/hiollama"]

# Set PYTHONPATH so imports work
ENV PYTHONPATH=/app

# Don't copy code - we'll mount it instead
# Run the application
CMD ["python", "-m", "hiollama"]