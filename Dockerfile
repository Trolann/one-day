FROM one-day-base:2024.7.3 AS app

WORKDIR /app

# Copy specific files and directories
COPY oneday.py settings.py requirements.txt ./
COPY outputs/ ./outputs/
COPY inputs/ ./inputs/
COPY dispatch/ ./dispatch/

# Copy the .env file from the host to the container
COPY .env .

# Reinstall requirements in case they've changed
RUN pip install --no-cache-dir -r requirements.txt

# Run the Python script
CMD ["python", "oneday.py"]