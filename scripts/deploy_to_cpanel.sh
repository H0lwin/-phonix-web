#!/usr/bin/env bash
# deploy_to_cpanel.sh
# Interactive deployment helper for Phonix project to cPanel environments.
# This script automates as much as possible of the deployment workflow.
# Notes:
# - Designed to run on a local machine or inside cPanel Terminal (bash-compatible shell).
# - It cannot click cPanel UI buttons; when a cPanel UI step is required it will pause and instruct the user.
# - For actions that require root access on a VPS (like installing Nginx), the script will print instructions instead.

set -euo pipefail
IFS=$'\n\t'

print_step() {
  echo
  echo "================================================================="
  echo "STEP: $1"
  echo "================================================================="
}

ask() {
  # ask question with default
  local prompt="$1"
  local default="$2"
  read -rp "$prompt [$default]: " val
  if [ -z "$val" ]; then
    echo "$default"
  else
    echo "$val"
  fi
}

confirm() {
  local prompt="$1"
  while true; do
    read -rp "$prompt (y/n): " yn
    case "$yn" in
      [Yy]*) return 0;;
      [Nn]*) return 1;;
      *) echo "Please answer y or n.";;
    esac
  done
}

# Defaults
REPO_URL="https://github.com/H0lwin/-phonix-web.git"
DEFAULT_APP_DIR="$PWD/phonix-dj"

print_step "Welcome"
cat <<EOF
This script helps automate deployment steps for the Phonix Django project targeting cPanel.
It will:
 - Clone the repository (or use existing folder)
 - Create a Python virtualenv
 - Install pip dependencies
 - Create a skeleton .env (you must edit secrets manually)
 - Run Django migrate and collectstatic
 - Create a simple passenger_wsgi.py

On cPanel, some steps (creating MySQL user via UI, enabling AutoSSL) must be done through the cPanel web UI. The script will pause and explain those.

Run this script in your local machine OR from the cPanel Terminal (if available).
EOF

if ! command -v git >/dev/null 2>&1; then
  echo "ERROR: git is not installed. Install git and re-run."
  exit 1
fi

# Prefer python3 if available
PYTHON_CMD=""
if command -v python3 >/dev/null 2>&1; then
  PYTHON_CMD=python3
elif command -v python >/dev/null 2>&1; then
  PYTHON_CMD=python
else
  echo "ERROR: python3 or python is not installed. Install Python 3.11+ and re-run."
  exit 1
fi

# Step 1: Clone
print_step "Clone repository"
read -rp "Repository URL (or ENTER for default ${REPO_URL}): " repoin
repoin=${repoin:-$REPO_URL}
read -rp "Target path to clone into (or ENTER for default ${DEFAULT_APP_DIR}): " target
target=${target:-$DEFAULT_APP_DIR}

if [ -d "$target" ] && [ -n "$(ls -A "$target")" ]; then
  echo "Target folder $target already exists and is not empty."
  if confirm "Do you want to pull latest changes instead of cloning?"; then
    cd "$target"
    git pull || true
  else
    echo "Please choose or empty the target folder and re-run."
    exit 1
  fi
else
  git clone "$repoin" "$target"
fi

cd "$target"

# Step 2: Create virtualenv
print_step "Virtualenv activation check"
# The user requested that the script assume a virtualenv is already created and activated.
# We'll detect VIRTUAL_ENV and prefer the venv's python if active. If not active, ask user to continue.
if [ -n "${VIRTUAL_ENV:-}" ]; then
  echo "Detected an active virtualenv: ${VIRTUAL_ENV}"
  # When venv is active, 'python' should point to the venv python; use that.
  PYTHON_CMD=python
else
  echo "No active virtualenv detected. This script assumes you have already created and activated a virtualenv."
  if confirm "Do you want to continue without an activated virtualenv? (not recommended)"; then
    echo "Continuing without active virtualenv. Make sure the chosen python has required packages."
    # PYTHON_CMD remains as detected (python3 or python)
  else
    echo "Please create and activate a virtualenv before running this script. Example: python3 -m venv venv; source venv/bin/activate"
    exit 1
  fi
fi

print_step "Install requirements"
if [ -f requirements.txt ]; then
  pip install --upgrade pip
  pip install -r requirements.txt || echo "pip install had errors; check logs above"
else
  echo "No requirements.txt found. Skipping pip install."
fi

# Step 3: Create .env skeleton
print_step "Create .env"
ENV_FILE=.env
if [ -f "$ENV_FILE" ]; then
  echo ".env already exists. Backing up to .env.bak"
  cp "$ENV_FILE" "${ENV_FILE}.bak"
fi

read -rp "Enter DJANGO_SECRET_KEY (or ENTER to generate a random one): " provided_key
if [ -z "$provided_key" ]; then
  provided_key=$(${PYTHON_CMD} - <<'PY'
import secrets
print(secrets.token_urlsafe(50))
PY
)
  echo "Generated random secret key"
fi

read -rp "Enter ALLOWED_HOSTS (comma-separated, e.g. yourdomain.com,www.yourdomain.com): " allowed_hosts
allowed_hosts=${allowed_hosts:-localhost}

read -rp "Enter DB_NAME (as created in cPanel): " db_name
read -rp "Enter DB_USER (as created in cPanel): " db_user
read -rp "Enter DB_PASSWORD (as created in cPanel): " db_pass

cat > "$ENV_FILE" <<EOF
DJANGO_SECRET_KEY=${provided_key}
DEBUG=False
ALLOWED_HOSTS=${allowed_hosts}
DB_NAME=${db_name}
DB_USER=${db_user}
DB_PASSWORD=${db_pass}
DB_HOST=localhost
DB_PORT=3306
EOF

echo ".env created at $PWD/$ENV_FILE"

# Function: sanitize ALLOWED_HOSTS (remove scheme prefixes)
sanitize_allowed_hosts() {
  local raw="$1"
  # remove http:// or https:// and trim whitespace
  echo "$raw" | sed -E 's#https?://##g' | sed -E 's/\s+//g'
}

# Function: ensure .env is UTF-8. If not, try common encodings with iconv.
ensure_env_utf8() {
  local f="$1"
  if ${PYTHON_CMD} - "$f" <<'PY' 2>/dev/null
import sys
try:
    open(sys.argv[1],'r',encoding='utf-8').read()
    sys.exit(0)
except Exception:
    sys.exit(1)
PY
  then
    return 0
  fi

  echo ".env is not valid UTF-8. Attempting to convert with iconv using common encodings..."
  local encs=("CP1256" "WINDOWS-1256" "ISO-8859-1" "CP1252" "ISO-8859-6")
  for enc in "${encs[@]}"; do
    if command -v iconv >/dev/null 2>&1; then
      if iconv -f "$enc" -t UTF-8 "$f" -o "${f}.utf8" 2>/dev/null; then
        mv "${f}.utf8" "$f"
        echo "Converted $f from $enc to UTF-8"
        return 0
      fi
    fi
  done

  echo "Automatic conversion failed or iconv not available. Please recreate .env with UTF-8 encoding." >&2
  return 1
}

# After creating .env, sanitize ALLOWED_HOSTS entry and rewrite file safely if needed
if [ -n "${allowed_hosts:-}" ]; then
  sanitized=$(sanitize_allowed_hosts "$allowed_hosts")
  if [ "$sanitized" != "$allowed_hosts" ]; then
    echo "Sanitized ALLOWED_HOSTS: $sanitized"
    # replace the ALLOWED_HOSTS line in the .env file
    if grep -q "^ALLOWED_HOSTS=" "$ENV_FILE"; then
      # Use sed to replace whole line
      sed -i.bak -E "s#^ALLOWED_HOSTS=.*#ALLOWED_HOSTS=${sanitized}#" "$ENV_FILE"
      echo "Backed up previous .env to ${ENV_FILE}.bak and updated ALLOWED_HOSTS"
    fi
  fi
fi

# Give user a chance to correct DB name/user to match cPanel (prefixes)
echo
echo "You said you created a database in cPanel. Often cPanel adds a prefix like username_."
echo "If the DB name or user you entered into .env doesn't match the actual cPanel names, update them now."
read -rp "Current DB_NAME in .env is '${db_name}'. Enter actual DB_NAME (or ENTER to keep): " real_db
if [ -n "$real_db" ]; then
  sed -i.bak -E "s#^DB_NAME=.*#DB_NAME=${real_db}#" "$ENV_FILE"
  echo "DB_NAME updated to $real_db"
  db_name=$real_db
fi
read -rp "Current DB_USER in .env is '${db_user}'. Enter actual DB_USER (or ENTER to keep): " real_user
if [ -n "$real_user" ]; then
  sed -i.bak -E "s#^DB_USER=.*#DB_USER=${real_user}#" "$ENV_FILE"
  echo "DB_USER updated to $real_user"
  db_user=$real_user
fi

# Ensure .env is UTF-8 before Django loads it
if ! ensure_env_utf8 "$ENV_FILE"; then
  echo "ERROR: .env is not UTF-8 and automatic conversion failed. Please recreate .env with UTF-8 encoding and re-run."
  exit 1
fi
# Step 4: Migrate and collectstatic
print_step "Run migrations and collectstatic"
# Use the active python interpreter (PYTHON_CMD may be 'python' inside venv)
${PYTHON_CMD} manage.py migrate --noinput || echo "migrate returned an error"
${PYTHON_CMD} manage.py collectstatic --noinput || echo "collectstatic returned an error"

# Step 5: Create passenger_wsgi.py if missing
print_step "Passenger WSGI"
if [ ! -f passenger_wsgi.py ]; then
  cat > passenger_wsgi.py <<'PY'
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'phonix.settings')
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
PY
  echo "passenger_wsgi.py created"
else
  echo "passenger_wsgi.py already exists. Skipping."
fi

# Step 6: Instructions for cPanel steps that require UI
print_step "cPanel manual steps"
cat <<'STEP'
Now you need to perform a few steps in the cPanel web UI (these cannot be fully automated by this script):
1) Create a MySQL database and user via cPanel -> MySQL® Databases. Make sure DB_NAME, DB_USER and DB_PASSWORD values in .env match exactly (cPanel often adds a prefix).
2) In cPanel -> Setup Python App, create or edit the application and point Application root to this project folder. Choose Python version (3.11+) and ensure virtualenv path matches venv created.
3) In the Setup Python App, use the provided terminal or "Enter to Virtual Environment" to run pip install -r requirements.txt if not already done.
4) Restart the application from Setup Python App.
5) Enable SSL via cPanel AutoSSL or Let's Encrypt in the SSL/TLS area.

After completing these UI steps, return to the terminal and press ENTER to continue.
STEP

read -rp "Press ENTER after completing the cPanel UI steps..." dummy

# Step 7: Final check
print_step "Final check"
echo "Attempting to run a quick check: ${PYTHON_CMD} manage.py check"
${PYTHON_CMD} manage.py check || echo "manage.py check returned errors"

echo
echo "Deployment helper finished. If the web UI shows errors, open cPanel -> Error Logs and share the trace."

echo "Done."
