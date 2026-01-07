# Use an official lightweight Python 3.11+ image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port Dash will run on
EXPOSE 8050

# Run the app using Gunicorn for production-grade serving
# Ensure 'server = app.server' is defined in your app.py
CMD ["gunicorn", "--bind", "0.0.0.0:8050", "app:server"]
