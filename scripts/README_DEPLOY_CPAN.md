deploy_to_cpanel.sh — README

Purpose

This repository contains an interactive Bash script `deploy_to_cpanel.sh` that automates most of the deployment steps for the Phonix Django project targeting cPanel environments. It is designed for beginners and for use either locally or in the cPanel Terminal (if available).

What the script does

- Clone the repository (or pull latest changes if folder exists)
- Create a Python virtual environment (`venv`)
- Install Python packages from `requirements.txt`
- Create a `.env` skeleton (prompts for DB credentials and generates secret key)
- Run `manage.py migrate` and `manage.py collectstatic`
- Create a `passenger_wsgi.py` if missing
- Pause and instruct the user to complete interactive cPanel steps (MySQL creation, Setup Python App configuration, enabling AutoSSL / SSL)

What the script cannot do (and why)

- Click buttons in the cPanel web UI (MySQL creation, Setup Python App creation, enabling AutoSSL). Those require either the cPanel web interface or cPanel UAPI calls with authentication tokens.
- Fully install system packages (e.g. `libmysqlclient-dev`); you must ask your hosting provider or use a VPS with root access.
- Configure Nginx on shared hosting. For Nginx you need a VPS with root privileges.

Prerequisites

- Bash shell (script uses bash features). cPanel Terminal provides a bash-like shell.
- Python 3.11 (or supported version) available on the host.
- Git must be available (for cloning) or you can upload the project ZIP from your local machine.

Quick start (run locally or in cPanel Terminal)

1. Make the script executable:

```bash
chmod +x scripts/deploy_to_cpanel.sh
```

2. Run it:

```bash
./scripts/deploy_to_cpanel.sh
```

3. Follow interactive prompts. When the script asks you to complete cPanel UI steps, open the cPanel web interface in your browser and perform the listed tasks.

Notes and troubleshooting

- If `pip install` fails for `mysqlclient`, consider editing `requirements.txt` to use `mysql-connector-python` (pure-Python) or ask hosting support to install the necessary system libraries.
- If Python version mismatch occurs, in cPanel Setup Python App choose the correct Python interpreter or use the cPanel Terminal to create the venv with the available Python.
- Keep a backup of `.env.bak` created by the script in case you need to restore any value.

Optional: automating cPanel API calls

cPanel provides UAPI/WHM API; if you have API tokens and the host allows it, you can automate database creation and other UI actions by calling cPanel UAPI endpoints. This script avoids embedding credentials and therefore leaves manual steps to reduce risk. If you want, I can extend the script to support UAPI calls (you'll need to provide a cPanel username and API token).

Security

- Do not commit `.env` to git, it contains secrets. Add `.env` to `.gitignore` if not already present.
- Generated secret keys are random and strong; keep them private.

Next steps I can help with

- Add UAPI support (automated DB creation) if you provide an API token and want automation.
- Create a PowerShell equivalent script if you'd prefer running from Windows PowerShell.
- Provide a step-by-step checklist tailored to your cPanel layout (screenshots and exact menu names).
