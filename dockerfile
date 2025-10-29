# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY main.py .

# Install Flask
RUN pip install flask

# Expose port 8000
EXPOSE 8000

# Run the app
CMD ["python", "main.py"]
