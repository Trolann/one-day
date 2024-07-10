FROM python:bookworm

WORKDIR /app

# Update apt and install git
RUN apt-get update && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

# Clone the repository
RUN git clone https://github.com/Trolann/one-day.git .

# Copy the .env file from the host to the container
COPY .env .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the Python script
CMD ["python", "oneday.py"]
