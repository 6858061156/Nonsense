# Thai Alphabet Drill

A quiz application to practice Thai alphabet with backend tracking of quiz starts.

## Setup

### Prerequisites
- Docker and Docker Compose (recommended)
- Or: Python 3.11+, PostgreSQL 12+

### Running with Docker Compose (Recommended)

```bash
docker-compose up
```

This will:
- Start a PostgreSQL database
- Start the Python Flask backend on http://localhost:5000
- Create the necessary database tables automatically

Open `index.html` in your browser. The app will connect to the backend at `http://localhost:5000`.

### Running Manually

1. **Set up PostgreSQL database:**
   ```bash
   createdb quiz_db
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Flask backend:**
   ```bash
   python app.py
   ```
   The backend will run on `http://localhost:5000`

4. **Open the frontend:**
   Open `index.html` in your browser

## Features

- Welcome screen asking for user nickname
- Quiz start counter persisted in PostgreSQL
- Counter displayed next to nickname during quiz
- Automatic marking of correct answers
- Remaining letter counter
- Offline mode fallback if backend is unavailable

## API Endpoints

- `POST /api/quiz/start` - Increment quiz start counter for a user
- `GET /api/user/<nickname>` - Get user quiz start count
- `GET /health` - Health check endpoint
