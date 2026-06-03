# Rajarata Kuppi Frontend - Split Version

Your original single HTML file has been broken into a cleaner frontend structure.

## Structure

```text
rajarata_kuppi_split/
├── index.html                 # Home page
├── student-material.html      # Student Material page
├── modules.html               # Modules page
├── notes.html                 # Notes page
├── gpa.html                   # GPA Calculator page
├── forum.html                 # Forum page
├── support.html               # Support Center page
├── profile.html               # Student Profile page
├── pastpapers.html            # Past Papers page
├── notifications.html         # Notifications page
├── assets/
│   ├── css/
│   │   └── styles.css         # All shared styling
│   └── js/
│       └── app.js             # Shared JavaScript functions
└── components/
    ├── sidebar.html           # Sidebar partial for future backend/templates
    └── topbar.html            # Topbar partial for future backend/templates
```

## How to run

Open `index.html` directly in a browser, or serve the folder with Python:

```bash
cd rajarata_kuppi_split
python -m http.server 8000
```

Then open `http://localhost:8000`.

## What changed

- The original single-page style sections were converted into separate HTML pages.
- Sidebar links now use normal `href` page navigation instead of `onclick="showPage(...)"`.
- CSS is moved to `assets/css/styles.css`.
- JavaScript is moved to `assets/js/app.js`.
- `components/sidebar.html` and `components/topbar.html` are included for later use with Flask, Django, Express, PHP, or another backend template system.

## Backend note

When you connect a Python backend later, the best next structure is:

```text
project/
├── app.py
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── student-material.html
│   └── ...
└── static/
    ├── css/styles.css
    └── js/app.js
```

The `components` folder can become backend template includes.
