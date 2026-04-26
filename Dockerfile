FROM python:3.10-slim

# Prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files explicitly
COPY . .

# Ensure the static folder has correct permissions
RUN chmod -R 755 /app/static

# Expose the port Cloud Run expects
EXPOSE 8080

# Use uvicorn to run the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
