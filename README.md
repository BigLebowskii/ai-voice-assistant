# AI Voice Assistant

A full-stack voice assistant application that leverages LiveKit for real-time communication, OpenAI for intelligent responses, and a PostgreSQL database for data persistence.

## Features

- Real-time voice communication
- AI-powered responses using OpenAI
- Voice-to-text and text-to-voice conversion
- Support room functionality for user assistance
- Modern React frontend with Vite
- Flask backend API

## Prerequisites

- Node.js (v20)
- Python 3.12
- PostgreSQL database
- LiveKit account
- OpenAI API key

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/ai-voice-assistant.git
cd ai-voice-assistant
```

### 2. Get LiveKit API Keys

1. Sign up for an account at [LiveKit](https://livekit.io/)
2. Create a new project
3. Generate API keys (you'll need both the API Key and API Secret)
4. Note down the LiveKit URL for your project

### 3. Set Up the PostgreSQL Database

```bash
# Create a new PostgreSQL database named 'assistant'
createdb assistant

# Or using psql:
psql
CREATE DATABASE assistant;
\q
```

### 4. Configure Backend Environment Variables

Create a `.env` file in the `backend` directory with the following variables:

```
OPENAI_API_KEY=your_openai_api_key
LIVEKIT_URL=your_livekit_url
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
PG_DBNAME=assistant
PG_USER=your_postgres_username
PG_PASSWORD=your_postgres_password
PG_HOST=localhost
PG_PORT=5432
```

### 5. Configure Frontend Environment Variables

Create a `.env` file in the `frontend` directory with the following variables:

```
VITE_LIVEKIT_URL=your_livekit_url
```

Note: The `VITE_LIVEKIT_URL` should be the same as the `LIVEKIT_URL` in your backend `.env` file.

### 6. Set Up the Backend

```bash
# Navigate to the backend directory
cd backend

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations (if applicable)
# python manage.py migrate
```

### 7. Set Up the Frontend

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install
```

### 8. Running the Application

You'll need to run both the backend servers and the frontend development server:

#### Backend Servers

Open two terminal windows:

```bash
# Terminal 1 - Run the main server
cd backend
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
python server.py
```

```bash
# Terminal 2 - Run the agent service
cd backend
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
python agent.py
```

#### Frontend Server

```bash
# Terminal 3 - Run the frontend development server
cd frontend
npm run dev
```

The application should now be running at `http://localhost:5173` (or the port specified by Vite).

## Application Structure

- `frontend/` - React/Vite frontend application
  - `src/components/` - React components
  - `src/App.jsx` - Main application component

- `backend/` - Flask backend application
  - `server.py` - Main server for handling LiveKit token generation and API endpoints
  - `agent.py` - Service for handling AI voice agent functionality

## Technologies Used

- **Frontend**:
  - React
  - Vite
  - LiveKit Components

- **Backend**:
  - Flask
  - OpenAI API
  - LiveKit Server SDK
  - PostgreSQL

## Troubleshooting

- **LiveKit Connection Issues**: Ensure your API keys are correct and that your LiveKit project is properly set up.
- **Database Connection Issues**: Verify your PostgreSQL credentials and ensure the database is running.
- **OpenAI API Issues**: Confirm your OpenAI API key is valid and has sufficient credits.

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
