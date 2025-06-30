FROM python:3.11-slim

WORKDIR /app

# Install only the non-standard dependencies
RUN pip install --no-cache-dir \
    ollama>=0.5.2 \
    rich \
# Create the calous directory for data persistence
RUN mkdir -p /root/calous

# Set up volume mount point
VOLUME ["/root/calous"]

# Set PYTHONPATH so imports work
ENV PYTHONPATH=/app

# Don't copy code - we'll mount it instead
# Run the application
CMD ["python", "-m", "calous"]