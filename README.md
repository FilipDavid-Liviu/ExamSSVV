# Agricultural Crop Rotation Management System

A web-based system for managing farm fields, crops, and historical harvests. Built with Python, FastAPI, and Jinja2 templates.

## Project Structure

The codebase is split cleanly into frontend and backend components following MVC principles:

- **`backend/`**
  - **`models/`**: Domain entities (`Field`, `Crop`, `Harvest`) built with Pydantic.
  - **`repository/`**: In-memory database storage and initial test data seeder.
  - **`services/`**: Core business logic, cascading deletes, and report generation.
  - **`routers/`**: FastAPI routes that handle web requests and form submissions.
  - **`main.py`**: The main FastAPI application entry point.
- **`frontend/`**
  - **`templates/`**: Jinja2 HTML files for rendering the UI.
- **`requirements.txt`**: Standard Python dependencies listing.

## How to Run the App

Follow these simple steps to get the app running locally after cloning the repository:

**1. Create and activate a virtual environment**
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Mac/Linux:
source .venv/bin/activate
```

**2. Install Dependencies**
```bash
pip install -r requirements.txt
```

**3. Start the Server**
```bash
uvicorn backend.main:app --reload
```

**4. Access the Application**
- **Web Interface:** Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.
- **API Docs:** Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to see the automatically generated Swagger UI.
