# Chemical Equipment Parameter Visualizer

A hybrid web + desktop application for visualizing and analyzing chemical equipment parameters from CSV data.

## Features

- **CSV Upload**: Upload CSV files containing equipment data (Web & Desktop)
- **Data Analysis**: Automatic calculation of summary statistics (count, averages, type distribution)
- **Visualizations**: Interactive charts using Chart.js (Web) and Matplotlib (Desktop)
- **History Management**: Stores and displays last 5 uploaded datasets
- **PDF Reports**: Generate PDF reports with summary statistics
- **Authentication**: Basic token-based authentication

## Tech Stack

### Backend
- Django 6.0.1
- Django REST Framework
- SQLite Database
- Pandas for data processing
- ReportLab for PDF generation

### Frontend (Web)
- React.js 18.2.0
- Chart.js 4.4.0
- Axios for API calls

### Frontend (Desktop)
- PyQt5 5.15.10
- Matplotlib 3.8.2

## Project Structure

```
myproject/
├── myproject/          # Django project settings
├── equipment/          # Main Django app with API endpoints
├── frontend/           # React web application
├── desktop_app/        # PyQt5 desktop application
├── sample_equipment_data.csv  # Sample CSV file
└── requirements.txt    # Python dependencies
```

## Installation

### Backend Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Run migrations:
```bash
cd myproject
python manage.py makemigrations
python manage.py migrate
```

3. Create a superuser (optional):
```bash
python manage.py createsuperuser
```

4. Start the Django server:
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000`

### Frontend (Web) Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The web app will be available at `http://localhost:3000`

### Desktop Application Setup

1. Ensure PyQt5 and matplotlib are installed (included in requirements.txt)

2. Run the desktop application:
```bash
python desktop_app/main.py
```

## API Endpoints

- `POST /api/equipment/auth/register/` - Register a new user
- `POST /api/equipment/auth/login/` - Login and get token
- `POST /api/equipment/upload/` - Upload CSV file (requires authentication)
- `GET /api/equipment/summary/<dataset_id>/` - Get summary statistics
- `GET /api/equipment/history/` - Get upload history (last 5)
- `GET /api/equipment/data/<dataset_id>/` - Get equipment data
- `GET /api/equipment/pdf/<dataset_id>/` - Generate PDF report

## CSV Format

The CSV file must contain the following columns:
- Equipment Name
- Type
- Flowrate
- Pressure
- Temperature

See `sample_equipment_data.csv` for an example.

## Usage

1. **Register/Login**: Create an account or login to get an authentication token
2. **Upload CSV**: Upload a CSV file with equipment data
3. **View Summary**: See summary statistics including averages and type distribution
4. **View Charts**: Visualize data with interactive charts
5. **View History**: Access previously uploaded datasets (last 5)
6. **Generate PDF**: Download a PDF report with all statistics

## Development Notes

- The backend automatically keeps only the last 5 datasets
- Authentication is required for all API endpoints except registration/login
- CORS is configured to allow requests from `http://localhost:3000`
- The desktop app uses the same API endpoints as the web app

## License

This project is created for internship screening purposes.
