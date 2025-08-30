# Weather Report Service

A FastAPI backend service that fetches time-series weather data from Open-Meteo API and generates Excel exports and PDF reports with charts.

## Features

- Fetches hourly temperature & humidity data from Open-Meteo API
- Stores data in SQLite database with unique constraints
- REST API endpoints with proper validation
- Excel export (.xlsx) of historical data
- PDF report generation with matplotlib charts
- Docker containerization
- Automatic API documentation (Swagger UI)

## API Endpoints

- `GET /health` - Health check
- `GET /weather-report?lat={lat}&lon={lon}&days={days}` - Fetch and store weather data
- `GET /export/excel?hours={hours}&lat={lat}&lon={lon}` - Download Excel file
- `GET /export/pdf?lat={lat}&lon={lon}&start={start}&end={end}` - Generate PDF report

## Quick Start

### Using Docker (Recommended)

```bash
# Build and run
docker build -t weather-app .
docker run -p 8000:8000 weather-app

# Or using docker-compose
docker-compose up --build




## For reference Git commands for pushing the code to Github

Open your terminal and run these commands for pushing your code to the github:

```bash
# Navigate to your project folder
cd /Users/nageshsingadi/Downloads/weather_report

# Initialize git
git init

# Add all files to git
git add .

# Commit the files
git commit -m "Initial commit: Complete weather report service with FastAPI, Excel/PDF exports"

# Adding your GitHub repository as remote code
git remote add origin https://github.com/SingadiNagesh-01/weather-report-service.git

# Pushing the code to GitHub commands
git branch -M main

git push -u origin main