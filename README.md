# Nginx Configuration Manager

This script facilitates the management of Nginx server configurations by providing the ability to add or delete virtual host configurations for primary domains and subdomains.

## Features

- Creates required document roots (/var/www/...) and log directories (/var/log/nginx/...).
- Generates Nginx server blocks with support for static files and PHP-FPM.
- Handles symbolic links automatically in /etc/nginx/sites-enabled/.
- Safe reload capability: Runs 'nginx -t' to test configuration syntax before reloading Nginx to prevent downtime.

--------------------------------------------------------------------------------

## Directory Structure Strategy

### Main Domain Setup (example.com)
- Log Directory: /var/log/nginx/example.com/example.com/
- Web Root: /var/www/example.com/example.com/
- Configuration File: /etc/nginx/sites-available/example.com
- Symbolic Link: /etc/nginx/sites-enabled/example.com

### Subdomain Setup (test.example.com)
Note: The main domain directory /var/www/example.com/ must exist prior to creating a subdomain.
- Log Directory: /var/log/nginx/example.com/test.example.com/
- Web Root: /var/www/example.com/test.example.com/
- Configuration File: /etc/nginx/sites-available/test.example.com
- Symbolic Link: /etc/nginx/sites-enabled/test.example.com

--------------------------------------------------------------------------------

## Usage

You can use either the Python or Bash version of the tool.

### Python Script (nginxconf.py)

Add Configuration:
  sudo python3 nginxconf.py -a example.com

Add Configuration and Reload Nginx:
  sudo python3 nginxconf.py -a example.com -r

Delete Configuration:
  sudo python3 nginxconf.py -d example.com

Delete Configuration and Reload Nginx:
  sudo python3 nginxconf.py -d example.com -r

--------------------------------------------------------------------------------

### Bash Script (nginxconf.sh)

Make the script executable before running:
  chmod +x nginxconf.sh

Add Configuration:
  sudo ./nginxconf.sh -a example.com

Add Configuration and Reload Nginx:
  sudo ./nginxconf.sh -a example.com -r

Delete Configuration:
  sudo ./nginxconf.sh -d example.com

Delete Configuration and Reload Nginx:
  sudo ./nginxconf.sh -d example.com -r

--------------------------------------------------------------------------------

## Prerequisites

- Debian/Ubuntu-based system with Nginx installed.
- PHP-FPM (Default socket path configured: unix:/var/run/php/php8.1-fpm.sock).
- Root or sudo execution privileges.

--------------------------------------------------------------------------------

## License

This script is licensed under the MIT License (LICENSE).
