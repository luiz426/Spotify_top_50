# Spotify Top 50 Tracker

This project uses Apache Airflow to automatically collect data from Spotify Brazil's top 50 songs, storing them in a PostgreSQL database for analysis and monitoring of music trends.

##  Objective

The main goal is to maintain an updated historical record of Spotify Brazil's most popular songs, enabling:
- Real-time monitoring of trending songs
- Historical analysis of artist and song popularity
- Tracking ranking changes over time

##  Architecture

The project is built using the following technologies:

- **Apache Airflow**: Data pipeline orchestration and automation
- **Python**: Main development language
- **PostgreSQL**: Storage database
- **Spotify API**: Data source through the `spotipy` library
- **Docker & Docker Compose**: Service containerization and management

### System Components

- **Airflow Webserver**: Web interface for DAG monitoring and management
- **Airflow Scheduler**: Task execution manager
- **Airflow Worker**: Task executor
- **PostgreSQL**: Database for Airflow and data storage
- **Redis**: Message broker for Airflow
- **PgAdmin**: Web interface for database management

##  How to Run

### Prerequisites

- Docker and Docker Compose installed
- Spotify Developer Credentials (Client ID and Client Secret)
- Minimum 4GB RAM available
- Minimum 2 CPUs
- Minimum 10GB disk space

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd spotify-top-50-tracker
```

2. Configure Spotify credentials in Airflow:
   - Access Airflow web interface (http://localhost:8080)
   - Go to Admin -> Connections
   - Add a new connection:
     - Conn Id: `spotify_credentials`
     - Conn Type: `Generic`
     - Extra: `{"client_id": "your-client-id", "client_secret": "your-client-secret"}`

3. Start services:
```bash
docker-compose up -d
```

##  Data Structure

Data is stored in the `top_tracks` table with the following structure:

- `position`: Current ranking position
- `track_id`: Unique Spotify track ID
- `name`: Song name
- `artist`: Main artist name
- `popularity`: Popularity index (0-100)
- `date_captured`: Collection date and time

##  Data Pipeline

The `spotify_top_50` DAG executes the following tasks:

1. `extract_spotify_data`: 
   - Connects to Spotify API
   - Collects top 50 songs data
   - Processes and structures data

2. `save_to_database`:
   - Receives processed data
   - Saves to PostgreSQL database

The pipeline runs hourly (`@hourly`), keeping data always up to date.

##  Accessing Data

### Via PgAdmin
- Access http://localhost:8081
- Login with configured credentials
- Connect to PostgreSQL server using:
  - Host: postgres
  - Port: 5432
  - Database: airflow
  - Username: airflow
  - Password: airflow

### Via SQL
```sql
SELECT *
FROM public.top_tracks
ORDER BY date_captured DESC, position ASC;
```

##  Monitoring

- **Airflow UI**: http://localhost:8080
  - Monitor DAG executions
  - Check logs
  - Manage tasks

- **PgAdmin**: http://localhost:8081
  - Explore stored data
  - Execute custom queries
  - Manage database

##  Security

- All sensitive passwords and credentials should be configured through environment variables or secrets
- Project uses only official Docker Hub images
- All exposed ports are configurable via docker-compose
