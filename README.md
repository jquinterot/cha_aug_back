# FastAPI Chat Scaffold

A best-practice FastAPI project for a chat app with OpenAI integration.

## Structure
- Modular folder layout
- Versioned API routes
- Models, schemas, and services separation
- Ready for OpenAI integration

## Getting Started (Local Development)

1. **Install Python 3.8+**
   - Download from [python.org](https://www.python.org/downloads/) if not already installed.
   - Check your version:
     ```bash
     python3 --version
     ```

2. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd <repo-directory>
   ```

3. **Create a virtual environment**
   ```bash
   python3 -m venv .venv
   ```

4. **Activate the virtual environment**
   - On macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```
   - On Windows:
     ```cmd
     .venv\Scripts\activate
     ```

5. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## How to run

Start the FastAPI server with:
```bash
uvicorn app.main:app --reload
```

The app will be available at [http://127.0.0.1:8000](http://127.0.0.1:8000)
