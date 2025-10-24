# Cardora - Credit Card Statement Analyzer

A FastAPI-based application for analyzing credit card statements using AI.

## Tech Stack

- **Backend:** Python 3.14 with FastAPI
- **Database:** PostgreSQL
- **AI:** Google Gemini API
- **Frontend:** React Native (coming soon)

## Project Structure

```
Cardora/
├── app/
│   ├── main.py              # Application entry point (like Program.cs)
│   ├── routers/             # API routes (like Controllers/)
│   ├── models/              # Data models and schemas
│   └── services/            # Business logic
├── venv/                    # Virtual environment (like packages/)
├── requirements.txt         # Dependencies (like .csproj)
├── .env                     # Environment variables (like appsettings.json)
└── README.md
```

## Setup Instructions

### 1. Prerequisites
- Python 3.11+ installed
- PostgreSQL installed and running

### 2. Create Virtual Environment
```bash
# Create venv
py -m venv venv

# Activate (Windows CMD)
venv\Scripts\activate.bat

# Activate (PowerShell)
venv\Scripts\Activate.ps1

# Activate (Git Bash/Linux)
source venv/Scripts/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
# Copy example env file
copy .env.example .env

# Edit .env with your values
# Add your Gemini API key, database credentials, etc.
```

### 5. Run the Application
```bash
# Development server with auto-reload
uvicorn app.main:app --reload

# Or specify host and port
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Access the API
- **API:** http://127.0.0.1:8000
- **Interactive Docs (Swagger):** http://127.0.0.1:8000/docs
- **Alternative Docs (ReDoc):** http://127.0.0.1:8000/redoc

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black app/
```

### Type Checking
```bash
mypy app/
```

## API Endpoints

- `GET /` - Welcome message
- `GET /health` - Health check

## For .NET Developers

If you're coming from .NET, here are the equivalents:

| .NET | Python |
|------|--------|
| `dotnet run` | `uvicorn app.main:app --reload` |
| `dotnet restore` | `pip install -r requirements.txt` |
| `.csproj` | `requirements.txt` |
| `Program.cs` | `app/main.py` |
| Controllers/ | routers/ |
| `[HttpGet]` | `@app.get()` |

## License

MIT
