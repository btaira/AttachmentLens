FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY app.py .
COPY templates/ templates/

# Create volume mount point for persistent data
VOLUME /app/data

# Expose port
EXPOSE 5000

# Run app
CMD ["python", "app.py"]
