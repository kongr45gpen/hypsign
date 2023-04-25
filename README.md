# hypsign

## Installation
First, set up a `venv` for your project.
```bash
python3 -m venv venv
source venv/bin/activate
```

Then, install project dependencies:
```bash
pip install -r requirements.txt
``` 

Then, apply the migrations:
```bash
python manage.py migrate
```

Override any local settings in `hypsign/local_settings.py`:
```python
# hypsign/local_settings.py
ALLOWED_HOSTS = ['*']
```

Finally, create a superuser:
```bash
python manage.py createsuperuser
```

and now run the development server:
```bash
python manage.py runserver
```