#!/usr/bin/env bash
# deploy_to_ubuntu.sh
# Interactive deployment helper for Phonix project on Ubuntu 22.04 with Apache
# This script automates the deployment workflow for a production environment
# targeting Ubuntu 22.04 with Apache web server and Gunicorn application server.

set -euo pipefail
IFS=$'\n\t'

# Global variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_FILE="/var/log/phonix_deploy.log"

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

# Logging functions
log_info() {
  echo "[INFO] $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

log_success() {
  echo "[SUCCESS] $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

log_warning() {
  echo "[WARNING] $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

log_error() {
  echo "[ERROR] $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_success() {
  echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
  echo -e "${YELLOW}! $1${NC}"
}

print_error() {
  echo -e "${RED}✗ $1${NC}"
}

print_info() {
  echo -e "${BLUE}ℹ $1${NC}"
}

# Error handling
error_exit() {
  log_error "$1"
  print_error "$1"
  exit 1
}

# Check if running as root
check_root() {
  if [[ $EUID -eq 0 ]]; then
    error_exit "This script should not be run as root. Please run as a regular user with sudo privileges."
  fi
}

# Check system requirements
check_system() {
  # Check Ubuntu version
  if ! command -v lsb_release >/dev/null 2>&1; then
    error_exit "lsb_release not found. This script is designed for Ubuntu."
  fi
  
  local ubuntu_version
  ubuntu_version=$(lsb_release -rs)
  if [[ ! "$ubuntu_version" =~ ^(20\.04|22\.04|24\.04)$ ]]; then
    log_warning "This script is tested on Ubuntu 22.04. Your version is $ubuntu_version. Proceeding anyway."
  else
    log_info "Ubuntu $ubuntu_version detected"
  fi
}

# Check if required commands are available
check_dependencies() {
  local deps=(git python3 pip virtualenv apache2 mysql)
  local missing_deps=()
  
  print_step "Checking system dependencies"
  
  for dep in "${deps[@]}"; do
    if ! command -v "$dep" >/dev/null 2>&1; then
      missing_deps+=("$dep")
    fi
  done
  
  if [ ${#missing_deps[@]} -ne 0 ]; then
    log_warning "Missing dependencies: ${missing_deps[*]}"
    if confirm "Do you want to install missing dependencies?"; then
      log_info "Updating package list"
      sudo apt update || error_exit "Failed to update package list"
      
      # Install missing packages
      for dep in "${missing_deps[@]}"; do
        case "$dep" in
          "virtualenv")
            log_info "Installing python3-virtualenv"
            sudo apt install -y python3-virtualenv || error_exit "Failed to install python3-virtualenv"
            ;;
          "mysql")
            log_info "Installing mysql-client"
            sudo apt install -y mysql-client || error_exit "Failed to install mysql-client"
            ;;
          *)
            log_info "Installing $dep"
            sudo apt install -y "$dep" || error_exit "Failed to install $dep"
            ;;
        esac
      done
    else
      error_exit "Please install the missing dependencies and re-run the script."
    fi
  fi
  
  log_success "All system dependencies are satisfied"
}

# Validate project structure
validate_project() {
  print_step "Validating project structure"
  
  # Check essential files
  local required_files=(
    "manage.py"
    "requirements.txt"
    "phonix/settings.py"
  )
  
  for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
      error_exit "Required file $file not found. Please run this script from the project root directory."
    fi
  done
  
  # Check essential directories
  local required_dirs=(
    "core"
    "registry"
    "vekalet"
  )
  
  for dir in "${required_dirs[@]}"; do
    if [ ! -d "$dir" ]; then
      error_exit "Required directory $dir not found. Please run this script from the project root directory."
    fi
  done
  
  log_success "Project structure validated"
}

# Defaults
REPO_URL="https://github.com/H0lwin/-phonix-web.git"
DEFAULT_APP_DIR="/var/www/phonix-dj"
DEFAULT_DOMAIN="yourdomain.com"

print_step "Welcome"
cat <<EOF
This script helps automate deployment steps for the Phonix Django project 
targeting Ubuntu 22.04 with Apache web server.

It will:
 - Install required system packages
 - Clone the repository (or use existing folder)
 - Create a Python virtualenv
 - Install pip dependencies
 - Create a proper .env file
 - Configure MySQL database
 - Run Django migrations and collectstatic
 - Set up Gunicorn systemd service
 - Configure Apache virtual host
 - Obtain SSL certificate with Let's Encrypt

Run this script on your Ubuntu 22.04 VPS as a regular user with sudo privileges.
EOF

# Check prerequisites
check_root
check_system
check_dependencies
validate_project

# Prefer python3 if available
PYTHON_CMD=""
if command -v python3 >/dev/null 2>&1; then
  PYTHON_CMD=python3
elif command -v python >/dev/null 2>&1; then
  PYTHON_CMD=python
else
  error_exit "python3 or python is not installed. Install Python 3.11+ and re-run."
fi

# Step 1: Clone or setup project directory
print_step "Setting up project directory"
read -rp "Repository URL (or ENTER for default ${REPO_URL}): " repoin
repoin=${repoin:-$REPO_URL}
read -rp "Target path to deploy to (or ENTER for default ${DEFAULT_APP_DIR}): " target
target=${target:-$DEFAULT_APP_DIR}

if [ "$target" != "$PROJECT_ROOT" ]; then
  if [ -d "$target" ] && [ -n "$(ls -A "$target")" ]; then
    echo "Target folder $target already exists and is not empty."
    if confirm "Do you want to pull latest changes instead of cloning?"; then
      cd "$target"
      git pull || error_exit "Failed to pull latest changes"
    else
      error_exit "Please choose an empty target folder or remove the existing content."
    fi
  else
    # Create parent directory if it doesn't exist
    sudo mkdir -p "$(dirname "$target")"
    # Clone with current user permissions
    log_info "Cloning repository from $repoin to $target"
    git clone "$repoin" "$target" || error_exit "Failed to clone repository"
    sudo chown -R $USER:$USER "$target"
  fi
else
  log_info "Using current directory as project root"
fi

cd "$target"
log_info "Working directory: $(pwd)"

# Step 2: Create virtualenv
print_step "Setting up Python virtual environment"
if [ ! -d "venv" ]; then
  log_info "Creating virtual environment"
  $PYTHON_CMD -m venv venv || error_exit "Failed to create virtual environment"
  log_success "Virtual environment created"
else
  log_warning "Virtual environment already exists"
fi

# Activate virtualenv
log_info "Activating virtual environment"
source venv/bin/activate
PYTHON_CMD=python

print_step "Installing Python dependencies"
if [ -f requirements.txt ]; then
  log_info "Upgrading pip"
  pip install --upgrade pip || error_exit "Failed to upgrade pip"
  
  log_info "Installing requirements from requirements.txt"
  pip install -r requirements.txt || error_exit "Failed to install requirements"
  
  # Install additional production dependencies
  log_info "Installing production dependencies"
  pip install gunicorn || error_exit "Failed to install gunicorn"
  
  log_success "Python dependencies installed"
else
  error_exit "No requirements.txt found. Cannot proceed."
fi

# Step 3: Create .env file
print_step "Configure environment variables (.env)"
ENV_FILE=.env
if [ -f "$ENV_FILE" ]; then
  log_warning ".env already exists. Backing up to .env.bak"
  cp "$ENV_FILE" "${ENV_FILE}.bak"
fi

read -rp "Enter your domain name (e.g. ${DEFAULT_DOMAIN}): " domain
domain=${domain:-$DEFAULT_DOMAIN}

# Validate domain name
if [[ ! "$domain" =~ ^[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,}$ ]]; then
  log_warning "Domain name format seems incorrect. Proceeding anyway."
fi

read -rp "Enter DJANGO_SECRET_KEY (or ENTER to generate a random one): " provided_key
if [ -z "$provided_key" ]; then
  log_info "Generating random secret key"
  provided_key=$(${PYTHON_CMD} - <<'PY'
import secrets
print(secrets.token_urlsafe(50))
PY
)
  log_info "Generated random secret key"
fi

# Database configuration
print_step "Database configuration"
echo "You need to have a MySQL database set up. If you haven't created one yet,"
echo "this script can help you set it up, but you'll need to provide root credentials."

read -rp "Enter DB_NAME (will be created if not exists): " db_name
read -rp "Enter DB_USER (will be created if not exists): " db_user
read -rp "Enter DB_PASSWORD for the user: " db_pass

# Validate inputs
if [ -z "$db_name" ] || [ -z "$db_user" ] || [ -z "$db_pass" ]; then
  error_exit "Database name, user, and password are required"
fi

# Try to connect to MySQL and set up database
if confirm "Do you want to set up the database now? (requires MySQL root access)"; then
  read -rp "Enter MySQL root user (usually 'root'): " mysql_root
  read -rsp "Enter MySQL root password: " mysql_root_pass
  echo
  
  if [ -z "$mysql_root" ] || [ -z "$mysql_root_pass" ]; then
    error_exit "MySQL root user and password are required"
  fi
  
  # Test connection first
  log_info "Testing MySQL connection"
  if ! mysql -u"$mysql_root" -p"$mysql_root_pass" -e "SELECT 1;" >/dev/null 2>&1; then
    error_exit "Cannot connect to MySQL with provided credentials"
  fi
  
  # Create database and user
  log_info "Creating database and user"
  mysql -u"$mysql_root" -p"$mysql_root_pass" <<MYSQL_SCRIPT
CREATE DATABASE IF NOT EXISTS \`${db_name}\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '${db_user}'@'localhost' IDENTIFIED BY '${db_pass}';
GRANT ALL PRIVILEGES ON \`${db_name}\`.* TO '${db_user}'@'localhost';
FLUSH PRIVILEGES;
MYSQL_SCRIPT
  
  if [ $? -eq 0 ]; then
    log_success "Database and user created successfully"
  else
    error_exit "Failed to create database. You may need to create it manually."
  fi
fi

# Create .env file
log_info "Creating .env file"
cat > "$ENV_FILE" <<EOF
# ============================================================================
# PHONIX PRODUCTION ENVIRONMENT CONFIGURATION
# Automatically generated on $(date)
# ============================================================================

# Django settings
SECRET_KEY=${provided_key}
DEBUG=False
ALLOWED_HOSTS=${domain},www.${domain}

# Database settings
DATABASE_ENGINE=django.db.backends.mysql
DATABASE_NAME=${db_name}
DATABASE_USER=${db_user}
DATABASE_PASSWORD=${db_pass}
DATABASE_HOST=localhost
DATABASE_PORT=3306

# Security settings
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

# Server settings
SERVER_HOST=127.0.0.1
SERVER_PORT=8000

# Additional settings for Phonix project
LANGUAGE_CODE=fa-ir
TIME_ZONE=Asia/Tehran
USE_TZ=False
EOF

log_info ".env created at $PWD/$ENV_FILE"

# Ensure .env has proper permissions
chmod 600 "$ENV_FILE"

# Step 4: Run migrations and collectstatic
print_step "Running Django migrations and collecting static files"
log_info "Loading environment variables"
export $(grep -v '^#' .env | xargs)

# Test database connection
log_info "Testing database connection"
if ! ${PYTHON_CMD} manage.py shell -c "from django.db import connection; connection.ensure_connection()" >/dev/null 2>&1; then
  log_warning "Cannot connect to database. Please check your database settings in .env"
fi

log_info "Running migrations"
${PYTHON_CMD} manage.py migrate --noinput || error_exit "Failed to run migrations"

log_info "Collecting static files"
${PYTHON_CMD} manage.py collectstatic --noinput -c || error_exit "Failed to collect static files"

log_success "Django setup completed"

# Step 5: Create Gunicorn systemd service
print_step "Setting up Gunicorn service"
GUNICORN_SERVICE="[Unit]
Description=Phonix Django Application
After=network.target

[Service]
Type=notify
User=$USER
Group=$USER
WorkingDirectory=$target
ExecStart=$target/venv/bin/gunicorn \\
    --workers=4 \\
    --worker-class=sync \\
    --bind=127.0.0.1:8000 \\
    --timeout=30 \\
    --log-level=info \\
    --log-file=/var/log/phonix_gunicorn.log \\
    phonix.wsgi:application
Restart=always
RestartSec=10
EnvironmentFile=$target/.env

[Install]
WantedBy=multi-user.target"

log_info "Creating systemd service file"
echo "$GUNICORN_SERVICE" | sudo tee /etc/systemd/system/phonix.service > /dev/null || error_exit "Failed to create systemd service file"
sudo systemctl daemon-reload
sudo systemctl enable phonix.service || log_warning "Failed to enable phonix service"

log_success "Gunicorn service configured"

# Step 6: Configure Apache virtual host
print_step "Configuring Apache virtual host"
APACHE_CONFIG="<VirtualHost *:80>
    ServerName ${domain}
    ServerAlias www.${domain}
    
    # Static files
    Alias /static/ $target/staticfiles/
    <Directory $target/staticfiles>
        Require all granted
        Options -Indexes
    </Directory>
    
    # Media files
    Alias /media/ $target/media/
    <Directory $target/media>
        Require all granted
        Options -Indexes
    </Directory>
    
    # Proxy to Gunicorn
    ProxyPreserveHost On
    ProxyPass /static/ !
    ProxyPass /media/ !
    ProxyPass / http://127.0.0.1:8000/
    ProxyPassReverse / http://127.0.0.1:8000/
    
    # Security headers
    Header always set Strict-Transport-Security \"max-age=31536000; includeSubDomains\"
    Header always set X-Content-Type-Options nosniff
    Header always set X-Frame-Options DENY
    
    ErrorLog \${APACHE_LOG_DIR}/phonix_error.log
    CustomLog \${APACHE_LOG_DIR}/phonix_access.log combined
    LogLevel warn
</VirtualHost>"

log_info "Creating Apache virtual host configuration"
echo "$APACHE_CONFIG" | sudo tee /etc/apache2/sites-available/phonix.conf > /dev/null || error_exit "Failed to create Apache configuration"

# Enable required Apache modules
log_info "Enabling required Apache modules"
sudo a2enmod proxy proxy_http headers rewrite ssl || error_exit "Failed to enable Apache modules"

# Enable the site
log_info "Enabling Phonix site"
sudo a2ensite phonix.conf || error_exit "Failed to enable Phonix site"

# Disable default site if requested
if confirm "Disable default Apache site?"; then
  log_info "Disabling default Apache site"
  sudo a2dissite 000-default.conf || log_warning "Failed to disable default site"
fi

log_success "Apache virtual host configured"

# Step 7: Set up SSL with Let's Encrypt
print_step "Setting up SSL certificate with Let's Encrypt"
if ! command -v certbot >/dev/null 2>&1; then
  log_warning "Certbot not found. Installing..."
  sudo apt update
  sudo apt install -y certbot python3-certbot-apache || error_exit "Failed to install Certbot"
fi

if confirm "Obtain SSL certificate with Let's Encrypt?"; then
  # Test Apache configuration first
  log_info "Testing Apache configuration"
  if sudo apache2ctl configtest; then
    log_info "Reloading Apache"
    sudo systemctl reload apache2
    
    # Run certbot
    log_info "Obtaining SSL certificate for $domain and www.$domain"
    sudo certbot --apache -d "$domain" -d "www.$domain" \
      --non-interactive --agree-tos --email "admin@$domain" || log_warning "Failed to obtain SSL certificate"
    
    if [ $? -eq 0 ]; then
      log_success "SSL certificate obtained and Apache configured"
    else
      log_warning "Failed to obtain SSL certificate. You may need to configure it manually."
    fi
  else
    error_exit "Apache configuration has errors. Please fix them before obtaining SSL certificate."
  fi
else
  log_warning "Skipping SSL setup. Remember to configure SSL manually."
fi

# Step 8: Set proper permissions
print_step "Setting file permissions"
# Create log directory
log_info "Creating log directory"
mkdir -p "$target/logs" || log_warning "Failed to create logs directory"

# Set ownership to www-data for Apache to serve static files
log_info "Setting file ownership"
sudo chown -R $USER:www-data "$target" || log_warning "Failed to set ownership"

# Make sure static files are readable
if [ -d "$target/staticfiles" ]; then
  log_info "Setting permissions for static files"
  chmod -R 755 "$target/staticfiles" || log_warning "Failed to set permissions for static files"
fi

if [ -d "$target/media" ]; then
  log_info "Setting permissions for media files"
  chmod -R 755 "$target/media" || log_warning "Failed to set permissions for media files"
fi

# Secure the project directory
log_info "Setting secure permissions for project files"
find "$target" -type d -exec chmod 755 {} \; || log_warning "Failed to set directory permissions"
find "$target" -type f -exec chmod 644 {} \; || log_warning "Failed to set file permissions"

# But keep .env secure
log_info "Securing .env file"
chmod 600 "$ENV_FILE" || log_warning "Failed to secure .env file"

# Set permissions for log files
if [ -d "$target/logs" ]; then
  log_info "Setting permissions for log files"
  chmod -R 755 "$target/logs" || log_warning "Failed to set permissions for logs directory"
  sudo chown -R $USER:www-data "$target/logs" || log_warning "Failed to set ownership for logs directory"
fi

# Step 9: Final checks and start services
print_step "Starting services and final checks"
# Create log files if they don't exist
log_info "Creating log files"
sudo touch /var/log/phonix_gunicorn.log || log_warning "Failed to create gunicorn log file"
sudo chown $USER:www-data /var/log/phonix_gunicorn.log || log_warning "Failed to set ownership for gunicorn log file"

# Start and enable Gunicorn service
log_info "Starting Phonix service"
sudo systemctl start phonix.service || log_warning "Failed to start phonix service"
sudo systemctl restart apache2 || error_exit "Failed to restart Apache"

# Run Django check
log_info "Running Django deployment check"
${PYTHON_CMD} manage.py check --deploy || log_warning "Django check returned warnings"

# Check service status
log_info "Checking service status"
if systemctl is-active --quiet phonix.service; then
  log_success "Gunicorn service is running"
else
  log_error "Gunicorn service is not running. Check with: sudo systemctl status phonix.service"
fi

if sudo systemctl is-active --quiet apache2; then
  log_success "Apache is running"
else
  error_exit "Apache is not running. Check with: sudo systemctl status apache2"
fi

# Step 10: Instructions for remaining steps
print_step "Post-deployment steps"
cat <<'STEP'
Remaining steps you might need to do manually:

1) Create a superuser:
   source venv/bin/activate
   python manage.py createsuperuser

2) Set up log rotation:
   Add to /etc/logrotate.d/phonix:
   /var/log/phonix/*.log {
       daily
       missingok
       rotate 52
       compress
       delaycompress
       notifempty
       create 644 www-data www-data
   }

   /var/log/phonix_gunicorn.log {
       daily
       missingok
       rotate 52
       compress
       delaycompress
       notifempty
       create 644 $USER www-data
   }

3) Set up database backups:
   Add to crontab (crontab -e):
   0 2 * * * /usr/bin/mysqldump -u DB_USER -p'DB_PASS' DB_NAME > /backups/phonix_$(date +\%Y\%m\%d).sql

4) Monitor logs:
   journalctl -u phonix -f
   tail -f /var/log/apache2/phonix_*.log
   tail -f /var/log/phonix_gunicorn.log

5) Set up monitoring (optional):
   Consider setting up uptime monitoring and performance monitoring.

Your Phonix application should now be accessible at:
https://${domain}

If you encounter any issues, check:
- Service status: sudo systemctl status phonix.service
- Apache logs: sudo tail -f /var/log/apache2/phonix_*.log
- Application logs: tail -f logs/*.log
- Gunicorn logs: tail -f /var/log/phonix_gunicorn.log
STEP

log_success "Deployment helper finished successfully!"
print_success "Deployment completed! Check the log file at $LOG_FILE for details."
echo "Done."