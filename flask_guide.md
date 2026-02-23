# BizOS Flask Setup Guide

This guide will help you set up the development environment for the BizOS Flask backend.

## 1. Prerequisites
- Python 3.10+
- PostgreSQL
- Redis

## 2. Setting Up the Virtual Environment
Create and activate a virtual environment to isolate your project dependencies:

```powershell
# Create the virtual environment
python -m venv venv

# Activate the virtual environment
.\venv\Scripts\activate
```

## 3. Installing Dependencies
Install the required libraries listed in `requirements.txt`:

```powershell
pip install -r requirements.txt
```

## 4. Environment Variables
Create a `.env` file in the root directory and add the following (replace with your values):

```env
FLASK_APP=manage.py
FLASK_ENV=development
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///bizos.db
REDIS_URL=redis://localhost:6379/0
ANTHROPIC_API_KEY=your-api-key
```

## 5. Initializing the Database
Once the code is implemented, you will run:

```powershell
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## 6. Running the Application
Start the Flask development server:

```powershell
flask run
```
