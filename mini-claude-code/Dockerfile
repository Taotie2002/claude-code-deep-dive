FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create workdir volume mount point
RUN mkdir -p workdir

CMD ["python", "main.py"]
