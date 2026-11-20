# CodeAlpha_ProjectManager — CodeAlpha Project Management Tool (Task 3)
Features: projects, kanban board, task assign, comments, notifications

## Run
```
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser   # optional, for /admin
python manage.py runserver
```
Open http://127.0.0.1:8000, register a user and start using it.
Tests: `python manage.py test`

Stack: Django, SQLite (can switch to MySQL in settings.py), Bootstrap 5.
