# Setup Instructions

## Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher and npm
- Git (for version control)

## Step-by-Step Setup

### 1. Backend Setup

```bash
# Navigate to project directory
cd myproject

# Install Python dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py makemigrations
python manage.py migrate

# (Optional) Create a superuser for Django admin
python manage.py createsuperuser

# Start the Django server
python manage.py runserver
```

The backend API will be running at `http://localhost:8000`

### 2. Frontend (Web) Setup

Open a new terminal:

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the React development server
npm start
```

The web application will be available at `http://localhost:3000`

### 3. Desktop Application Setup

Open a new terminal (ensure backend is running):

```bash
# Run the desktop application
python desktop_app/main.py
```

## Quick Start (Windows)

You can use the provided batch files:

1. **start_backend.bat** - Starts Django backend server
2. **start_frontend.bat** - Starts React frontend (in a new terminal)
3. **start_desktop.bat** - Starts PyQt5 desktop app

## Testing the Application

1. **Register/Login**: 
   - Open the web app or desktop app
   - Register a new account or login with existing credentials

2. **Upload CSV**:
   - Use the provided `sample_equipment_data.csv` file
   - Upload it through the web or desktop interface

3. **View Results**:
   - Summary statistics will be displayed
   - Charts will show visualizations
   - Data table will display all equipment

4. **Generate PDF**:
   - Click "Generate PDF Report" button
   - PDF will be downloaded with all statistics

## API Testing

You can test the API endpoints using tools like Postman or curl:

```bash
# Register a user
curl -X POST http://localhost:8000/api/equipment/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}'

# Login
curl -X POST http://localhost:8000/api/equipment/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}'

# Upload CSV (replace TOKEN with your token)
curl -X POST http://localhost:8000/api/equipment/upload/ \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -F "file=@sample_equipment_data.csv"
```

## Troubleshooting

### Backend Issues

- **Port 8000 already in use**: Change the port with `python manage.py runserver 8001`
- **Migration errors**: Delete `db.sqlite3` and run migrations again
- **Module not found**: Ensure all dependencies are installed with `pip install -r requirements.txt`

### Frontend Issues

- **Port 3000 already in use**: React will prompt to use another port
- **npm install fails**: Try deleting `node_modules` and `package-lock.json`, then run `npm install` again
- **CORS errors**: Ensure backend CORS settings allow `http://localhost:3000`

### Desktop App Issues

- **PyQt5 import error**: Install with `pip install PyQt5`
- **Connection refused**: Ensure Django backend is running on port 8000
- **Authentication error**: Make sure you're logged in through the desktop app

## Project Structure

```
myproject/
├── myproject/              # Django project settings
│   ├── settings.py        # Main settings file
│   └── urls.py            # URL routing
├── equipment/              # Main Django app
│   ├── models.py          # Database models
│   ├── views.py           # API views
│   ├── urls.py            # App URLs
│   └── admin.py           # Admin configuration
├── frontend/               # React web application
│   ├── src/
│   │   ├── App.js         # Main app component
│   │   └── components/    # React components
│   └── package.json       # Node dependencies
├── desktop_app/            # PyQt5 desktop application
│   └── main.py           # Desktop app entry point
├── sample_equipment_data.csv  # Sample data file
└── requirements.txt       # Python dependencies
```

## Next Steps

1. Test all features (upload, view, charts, PDF)
2. Customize the UI/UX as needed
3. Add additional features if required
4. Deploy to production when ready
