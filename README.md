# DevVault

A knowledge and asset management hub for small game-dev teams — built with
Django using Vertical Slice Architecture, connected to Supabase PostgreSQL.

## Local setup

```bash
# 1. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure the database
#    Copy .env.example to .env and fill in your own Supabase DATABASE_URL
#    (Supabase Dashboard -> Connect -> Direct tab -> Session pooler).
#    If you skip this step, Django falls back to local SQLite automatically.
cp .env.example .env

# 4. Check the configuration, then create + apply migrations
python manage.py check
python manage.py makemigrations
python manage.py migrate

# 5. Create an admin account (this row is written to Supabase)
python manage.py createsuperuser

# 6. Run the dev server
python manage.py runserver
```

Then visit:
- `http://127.0.0.1:8000/register/` — Register
- `http://127.0.0.1:8000/login/` — Login
- `http://127.0.0.1:8000/` — Home (requires login)
- `http://127.0.0.1:8000/profile/` — Profile (requires login)
- `http://127.0.0.1:8000/settings/` — Settings (requires login)

Registering an account automatically creates a Profile, a UserSettings
row, and your first **Workspace** — the Home screen reads its stats and
recent activity from whatever workspace your account belongs to.

After registering or updating your data, open the Supabase Dashboard ->
**Table Editor** to confirm rows exist in `auth_user`, `profile_profile`,
`user_settings_usersettings`, and `home_workspace`.

## Project layout (vertical slices)

```
devvault/
├── manage.py
├── .env                          # not committed — see .env.example
├── requirements.txt
├── devvault/                     # project config only — no business logic
│   ├── settings.py               # reads DATABASE_URL from .env
│   ├── urls.py                   # includes each feature's own urls.py
│   └── wsgi.py / asgi.py
│
├── apps/
│   ├── login/                    # Screen: Login
│   │   ├── forms.py, views.py, urls.py
│   ├── register/                 # Screen: Register
│   │   ├── forms.py, views.py, urls.py
│   ├── home/                     # Screen: Home
│   │   ├── models.py             #   Workspace, Membership, Tag, Entry, Comment
│   │   ├── views.py, urls.py, admin.py
│   ├── profile/                  # Screen: Profile
│   │   ├── models.py             #   Profile (display name, bio, avatar)
│   │   ├── forms.py, views.py, urls.py, admin.py, signals.py
│   └── user_settings/            # Screen: Settings
│       ├── models.py             #   UserSettings (dark mode, notifications, layout)
│       ├── forms.py, views.py, urls.py, admin.py, signals.py
│
├── templates/
│   ├── base.html                 # shared navbar + design system
│   ├── login/login.html
│   ├── register/register.html
│   ├── home/home.html
│   ├── profile/profile.html
│   └── user_settings/settings.html
│
├── static/
│   ├── css/{login,register,home,profile,user_settings,shared}/
│   ├── js/{login,register,home,profile,user_settings}/
│   └── images/{login,register,home,profile,user_settings}/
│
└── media/                        # uploaded profile pictures & entry images
```

Each slice owns everything it needs end to end — its own views, URLs,
templates, and static assets. Login and Register only import Django's
built-in User model; Register additionally creates the user's first
Profile/Settings/Workspace rows right after signup (the one deliberate
cross-feature touch point, documented in `apps/register/views.py`).
Home, Profile, and Settings never import from each other.
