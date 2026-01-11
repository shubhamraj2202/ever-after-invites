# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory in container
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY server.py .
COPY config.py .
COPY models.py .
COPY config.json .
COPY index.html .
COPY admin.html .
COPY admin.css .
COPY styles.css .
COPY config-loader.js .
COPY admin-client.js .

# Copy assets and themes directories
COPY assets/ ./assets/
COPY themes/ ./themes/

# Expose port (Cloud Run will set PORT env variable, default to 8080)
EXPOSE 8080

# Set environment variables for production
ENV HOST=0.0.0.0
ENV PORT=8080
ENV DEBUG=False

# Run the application
CMD ["python", "server.py"]
