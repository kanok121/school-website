# Mojidpur Central School — School Management Website

A complete school management system (with database) including:

- Dashboard (Institute ID, academic year, total students/teachers/classes)
- Student management (add/edit/delete, with photo upload, filter by class)
- Teacher management (add/edit/delete)
- Class & section management
- Student attendance (by date and class)
- Teacher attendance (by date)
- Login system (secured with username/password)
- REST API (JSON) for use from a mobile app

---

## 1. How to run it on your computer

### Step 1: Install Python
If you don't already have Python 3.10+, install it from [python.org](https://python.org).

### Step 2: Install the required packages
Open a terminal/command prompt in this folder and run:

```bash
pip install -r requirements.txt
```

### Step 3: Start the website

```bash
python app.py
```

On first run, it automatically creates a `school.db` database file and a default admin user.

### Step 4: Open it in your browser
```
http://localhost:5000
```
**Default login:**
- Username: `admin`
- Password: `admin123`

⚠️ Change the password after your first login (or update it directly in the database) — this is important for security.

---

## 2. Using it from mobile (same WiFi)

1. Find the IP address of the computer running the server:
   - Windows: run `ipconfig`, look for "IPv4 Address" (e.g. 192.168.0.105)
   - Mac/Linux: run `ifconfig` or `ip a`
2. Make sure your mobile and computer are on the same WiFi network.
3. On your mobile browser, go to:
   ```
   http://<computer's IP>:5000
   ```
   Example: `http://192.168.0.105:5000`

---

## 3. Going live on the internet (Deploy)

To make the website accessible to everyone even when your computer is off, host it on a hosting service. Simple, free options:

- **Render.com** — free tier for Flask apps
- **Railway.app** — easy deployment, free tier available
- **PythonAnywhere.com** — popular for Flask apps, free tier available

The general process for each:
1. Upload the code to GitHub
2. Create an account on the hosting site and connect your GitHub repo
3. Use `gunicorn app:app` as the start command (add `gunicorn` to `requirements.txt` for production)
4. After deployment, you'll get a public link (e.g. `https://mojidpur-school.onrender.com`) that opens from any mobile or computer

**Important:** Before going live, change `SECRET_KEY` and `SCHOOL_API_KEY` in `app.py` to complex/random values (best set as environment variables).

---

## 4. Using it as an API from a mobile app

You can build a separate mobile app (Android/iOS) that pulls data from this same database via the REST API. Every API call must include the API key in the header:

```
X-API-KEY: mojidpur-secret-key-2026
```
(change this in the `SCHOOL_API_KEY` variable in `app.py`)

### API Endpoints

| Method | URL | Purpose |
|---|---|---|
| GET | `/api/v1/dashboard` | Summary info |
| GET | `/api/v1/students` | List all students (filter with `?class_id=1`) |
| POST | `/api/v1/students` | Add a new student (JSON body) |
| GET | `/api/v1/teachers` | List all teachers |
| GET | `/api/v1/attendance/students?date=2026-07-26` | Student attendance for a given date |
| POST | `/api/v1/attendance/students` | Mark student attendance (JSON body) |
| GET | `/api/v1/attendance/teachers?date=2026-07-26` | Teacher attendance for a given date |
| POST | `/api/v1/attendance/teachers` | Mark teacher attendance |

### Example (testing with curl):

```bash
curl -H "X-API-KEY: mojidpur-secret-key-2026" http://localhost:5000/api/v1/students
```

To mark student attendance:
```bash
curl -X POST -H "X-API-KEY: mojidpur-secret-key-2026" -H "Content-Type: application/json" \
  -d '{"student_id": 1, "date": "2026-07-26", "status": "Present"}' \
  http://localhost:5000/api/v1/attendance/students
```

From a mobile app (Flutter/React Native/Android Studio, etc.) you can send HTTP requests to these same URLs to read/write data. Just replace `localhost:5000` with your server's actual address (IP or domain).

---

## 5. File structure

```
school_website/
├── app.py                  # Main application (routes, API, database models)
├── requirements.txt        # Required package list
├── school.db                # SQLite database (auto-created on first run)
├── static/
│   ├── style.css
│   └── uploads/             # Uploaded photos are stored here
└── templates/               # All HTML pages
```

---

## 6. Ideas for future additions

- Exam/result management module
- Fee management
- SMS notifications (attendance/results to guardians)
- ID card / routine generation
- Multi-user roles (teachers logging in to manage only their own class's attendance)

This base structure makes it easy to add any of these — just let me know which one you need first.
