# Hostel AI

A Django-based hostel complaint management system with role-based logins,
AI-assisted severity prediction, hidden internal department routing, an
automated alert/notification workflow, and a management analytics dashboard.

## ⚠️ A note on "Gemini 3.5 / Gemini 3.1 Flash-lite"

Your outline named "Gemini 3.5" and "Gemini 3.1 Flash-lite" as the model to
use. Those aren't published Google model names (the real Gemini lineup is
things like `gemini-1.5-flash`, `gemini-2.0-flash`, `gemini-2.5-flash`,
etc.), so I couldn't wire up a model that doesn't exist. Instead:

- **By default**, severity prediction runs on a small **offline
  scikit-learn classifier** (TF-IDF + Logistic Regression) trained on a
  synthetic hostel-complaint dataset baked into the repo
  (`complaints/ml/train_severity_model.py`). It ships already trained
  (`severity_model.joblib`), needs no API key, and works with zero
  internet access — good for running/demoing this project anywhere.
- **If you do have a real Gemini API key** and want the LLM to do the
  classification instead, open `hostel_ai/settings.py` and set:
  ```python
  SEVERITY_ENGINE = "gemini"
  GEMINI_API_KEY = "your-key-here"
  GEMINI_MODEL = "gemini-1.5-flash"  # or another real, current model name
  ```
  then `pip install google-generativeai`. The code automatically falls
  back to the local model if the Gemini call fails for any reason.

## Features implemented

1. **Role-based login** — Student, Warden, Management, Parent, Admin, each
   with its own dashboard and permissions.
2. **AI severity prediction** — every complaint is scored High/Medium/Low
   automatically at submission time.
3. **Smart complaint processing** — a keyword-based internal "department"
   detector (Electrical, Plumbing, Food & Mess, Cleanliness, Security,
   Internet & Wi-Fi, Furniture, General) runs behind the scenes and is
   **never shown in the UI** — it's only used to auto-assign the right
   warden.
4. **Real-time-style alerts** — the moment a complaint is submitted,
   Management, the auto-assigned Warden, and the student's linked Parent
   (never the student) get a notification with student name, room number,
   and severity.
5. **Admin analytics dashboard** — severity and status charts (Chart.js)
   plus a full complaint table, on the Management dashboard.
6. **Optional image upload** — students can attach a photo as proof.
7. **Database** — everything (users, complaints, severity, images,
   notifications, status history) lives in SQLite by default, zero setup.
8. **Automated workflow** — submit → AI scores severity + hidden
   department → stored → alerts fired → warden updates status → student
   + parent + management get notified → dashboards refresh automatically.
9. A complaint shows as **"My Complaint"** to the student who filed it,
   and **"New Complaint"** to any Warden/Management viewer who hasn't
   opened it yet (flips to a plain "Complaint" once they have).
10. **Admin** role gets full CRUD over every table via Django's built-in
    `/admin/` panel.

## Project layout

```
hostel_ai_project/
├── manage.py
├── requirements.txt
├── hostel_ai/          # settings, urls, wsgi/asgi
├── accounts/           # custom User model (role field), login/register
├── complaints/         # Complaint model, AI severity + routing, views
│   └── ml/              # the local severity classifier + training script
├── templates/
├── static/
└── media/              # uploaded complaint photos
```

## Setup

```bash
# 1. Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run database migrations
python manage.py makemigrations
python manage.py migrate

# 4. (Optional but recommended) create one demo account per role
python manage.py seed_demo_data
#    -> creates admin_demo / management_demo / warden_electrical /
#       warden_general / parent_demo / student_demo, all with password:
#       HostelAI@123

# 5. (Optional) create your own superuser for /admin/ instead
python manage.py createsuperuser

# 6. Run the server
python manage.py runserver
```

Then open **http://127.0.0.1:8000/** and log in. New students/wardens/
management/parents can also self-register at **/accounts/register/**.

The severity model already ships pre-trained. If you edit
`complaints/ml/train_severity_model.py`'s `TRAINING_DATA`, retrain with:

```bash
python manage.py train_severity_model
```

## Demo accounts (after `seed_demo_data`)

| Role       | Username            | Password       |
|------------|----------------------|----------------|
| Admin      | admin_demo           | HostelAI@123   |
| Management | management_demo      | HostelAI@123   |
| Warden     | warden_electrical    | HostelAI@123   |
| Warden     | warden_general       | HostelAI@123   |
| Parent     | parent_demo          | HostelAI@123   |
| Student    | student_demo         | HostelAI@123   |

`student_demo` already has 3 sample complaints so you can see severity
scoring, warden assignment, and the analytics dashboard immediately.

## Notes / things you may want to extend later

- A parent currently links to **one** student account (`User.parent`),
  chosen at registration time from a dropdown of parent accounts. You'd
  add a many-to-many if a parent needs multiple children.
- Warden auto-assignment picks the first active warden whose `department`
  matches (falling back to a "General" warden). For a real hostel you'd
  probably want load-balancing across multiple wardens per department.
- `DEBUG = True` and `SECRET_KEY` are dev defaults in `settings.py` —
  change both before deploying anywhere public.
