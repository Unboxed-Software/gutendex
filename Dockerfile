# Use an official lightweight Python runtime as a parent image
FROM python:3.10-slim

# Prevents Python from writing .pyc files to disk and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies required for psycopg2 and others
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for leveraging Docker layer caching
COPY requirements.txt /app/

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project code
COPY . /app/

# Collect static files into STATIC_ROOT (this directory will be created at runtime)
# We'll run collectstatic in the entrypoint or via docker-compose commands

# Expose port (Gutendex default Django port is 8000)
EXPOSE 8000

# Default entrypoint: run migrations, collectstatic, then start the server.
# In production, you’d typically use Gunicorn; for simplicity, we can show both options.
# Here’s an example entrypoint script approach:

COPY ./entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "gutendex.wsgi:application", "--bind", "0.0.0.0:8000"]
