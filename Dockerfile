FROM python:3.10-slim

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install MySQL client
RUN apt update && apt install -y default-mysql-client

# Copy the rest of the application
COPY . .

# Make startup script executable
RUN chmod +x startup.sh

EXPOSE 8000

ENTRYPOINT ["./startup.sh"]
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "run:app"]
