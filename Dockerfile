FROM python:3.9-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Create necessary directories
RUN mkdir -p storage/logs storage/job_results

# Set environment variables
ENV PYTHONPATH=/app

# Run the CLI with arguments passed to the container
ENTRYPOINT ["python", "-m", "cli.cli"]
CMD ["--help"]