This script facilitates the management of Nginx server configurations by providing the ability to add or delete configurations for domains and subdomains.

### Main Domain Setup

If a main domain name, like `gryptokali.com`, is provided, the script will:

- Create the log directory at `/var/log/nginx/gryptokali.com/`
- Create the web directory at `/var/www/gryptokali.com/gryptokali.com/`
- Generate the Nginx configuration file at `/etc/nginx/sites-available/gryptokali.com`
- Create a symbolic link in `/etc/nginx/sites-enabled/` to enable the site

### Subdomain Setup

If a subdomain, like `test.gryptokali.com`, is provided, the script will:

- Check if the main domain directory `/var/www/gryptokali.com/` exists
- If the main domain directory exists, it will:
  - Create the log directory at `/var/log/nginx/gryptokali.com/test.gryptokali.com/`
  - Create the web directory at `/var/www/gryptokali.com/test.gryptokali.com/`
  - Generate the Nginx configuration file at `/etc/nginx/sites-available/test.gryptokali.com`
  - Create a symbolic link in `/etc/nginx/sites-enabled/` to enable the subdomain site
  - 
## Usage

### Add Configuration

```bash
python3 nginxconf.py -a domain.com

```
### Delete Configuration

```bash
python3 nginxconf.py -d domain.com
```
### Delete and Restart nginx

```bash
python3 nginxconf.py -d domain.com -r
```


