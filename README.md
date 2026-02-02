# Chemical Equipment Parameter Visualizer

A hybrid application that runs both in the browser and as a desktop app. You upload a CSV of chemical equipment (name, type, flowrate, pressure, temperature), and the app parses it, computes summary stats, and shows tables and charts. The same Django API backs the React web UI and the PyQt5 desktop client.

This was built as an internship screening task—the goal was to show one backend, two frontends, and a clear path from upload to visualization and PDF reports.

---

## What it does

You get a single backend that:

- Accepts CSV uploads (web and desktop).
- Validates and parses rows with Pandas, then stores them in SQLite.
- Exposes a REST API for summary stats (totals, averages, equipment type breakdown).
- Keeps only the last 5 uploaded datasets as “history.”
- Serves PDF reports for any of those datasets.

The **web app** (React + Chart.js) and the **desktop app** (PyQt5 + Matplotlib) both talk to that API: login, upload, view tables and charts, switch between recent datasets, and download PDFs. So you can use whichever client you prefer.

Authentication is token-based (register/login); everything except auth endpoints requires a valid token.

---

## Tech stack

| Layer        | Technology                    | Role                          |
|-------------|-------------------------------|-------------------------------|
| Backend     | Django, Django REST Framework | API, auth, CSV handling       |
| Data        | Pandas, SQLite                | Parsing, storage               |
| PDF         | ReportLab                     | Report generation             |
| Web UI      | React, Chart.js, Axios        | Tables, charts, API calls      |
| Desktop UI  | PyQt5, Matplotlib             | Same flows, native app        |

The repo includes a `sample_equipment_data.csv` so you can try the flow without preparing your own file.

---

## What you need

- Python 3.8+ (for Django, PyQt5, Pandas, etc.)
- Node.js and npm (for the React frontend)
- Git (for cloning and version control)

---

## Getting started

All commands below assume you’re in the project root (where `manage.py`, `requirements.txt`, and the `frontend` folder live).

**1. Backend**

```bash
pip install -r requirements.txt
cd myproject
python manage.py migrate
python manage.py runserver
```

Leave that running. The API is at `http://localhost:8000`.

**2. Web app** (new terminal)

```bash
cd frontend
npm install
npm start
```

The app will open at `http://localhost:3000`. Register, log in, then upload `sample_equipment_data.csv` (or your own CSV with the same columns).

**3. Desktop app** (optional, new terminal; backend must be running)

```bash
python desktop_app/main.py
```

Log in with the same credentials you used in the web app. Upload and history work the same way; charts and tables are rendered with Matplotlib and PyQt5.

---

## CSV format

The backend expects a CSV with these column names (order doesn’t matter):

- **Equipment Name** — string
- **Type** — e.g. Reactor, Pump, Heat Exchanger
- **Flowrate** — number
- **Pressure** — number
- **Temperature** — number

If a column is missing or the types don’t match, the API returns a clear error. Use `sample_equipment_data.csv` as a reference.

---

## API overview

Base URL: `http://localhost:8000/api/equipment/`

| Method | Endpoint                    | Auth  | Description                    |
|--------|-----------------------------|-------|--------------------------------|
| POST   | `auth/register/`            | No    | Register; returns token        |
| POST   | `auth/login/`               | No    | Login; returns token           |
| POST   | `upload/`                   | Token | Upload CSV (multipart)         |
| GET    | `summary/<dataset_id>/`     | Token | Summary stats for a dataset    |
| GET    | `history/`                  | Token | Last 5 datasets (id, name, etc.)|
| GET    | `data/<dataset_id>/`        | Token | Full equipment rows            |
| GET    | `pdf/<dataset_id>/`         | Token | PDF report (binary response)   |

After login or register, send the token in the header: `Authorization: Token <your_token>`.

---

## Project layout

```
myproject/
├── myproject/           # Django project (settings, main urls)
├── equipment/           # App: models, API views, auth, URLs
├── frontend/            # React app (components, Chart.js, etc.)
├── desktop_app/         # PyQt5 app (main.py)
├── sample_equipment_data.csv
├── requirements.txt
└── README.md
```

The `equipment` app holds the Dataset/Equipment models, upload logic, summary and history endpoints, and PDF generation. Both frontends are thin clients over this API.

---

## Notes

- **History:** Only the 5 most recent uploads are kept. Older datasets are removed on the next upload.
- **CORS:** Allowed origin is `http://localhost:3000` so the React dev server can call the API.
- **Desktop threads:** API calls from the desktop app run in background threads and are cleaned up when done, so you shouldn’t see “QThread destroyed while still running” during login or upload.

If you hit issues, check that the backend is on port 8000 and the web frontend is on 3000, and that your CSV column names match exactly (including spelling and spaces).

---

*Built for an internship screening task. Django + React + PyQt5, one API, two clients.*
