This script facilitates the management of Nginx server configurations by providing the ability to add or delete configurations for domains and subdomains.

### Main Domain Setup

If a main domain name, like `example.com`, is provided, the script will:

- Create the log directory at `/var/log/nginx/example.com/example.com/`
- Create the web directory at `/var/www/example.com/example.com/`
- Generate the Nginx configuration file at `/etc/nginx/sites-available/example.com`
- Create a symbolic link in `/etc/nginx/sites-enabled/` to enable the site

### Subdomain Setup

If a subdomain, like `test.example.com`, is provided, the script will:

- Check if the main domain directory `/var/www/example.com/` exists
- If the main domain directory exists, it will:
  - Create the log directory at `/var/log/nginx/example.com/test.example.com/`
  - Create the web directory at `/var/www/example.com/test.example.com/`
  - Generate the Nginx configuration file at `/etc/nginx/sites-available/test.example.com`
  - Create a symbolic link in `/etc/nginx/sites-enabled/` to enable the subdomain site

## Usage (Python)

To add a configuration, use the following command: 

`sudo python3 nginxconf.py -a domain.com`

To delete a configuration, use the following command: 

`sudo python3 nginxconf.py -d domain.com`

To delete a configuration and restart Nginx, use the following command: 

`sudo python3 nginxconf.py -d domain.com -r`

## Usage (Bash)

Before using the Bash script, make sure it is executable by running:

`sudo chmod +x nginxconf.sh`

To add a configuration using the Bash script, use the following command: 

`sudo bash nginxconf.sh -a domain.com`

To delete a configuration using the Bash script, use the following command: 

`sudo bash nginxconf.sh -d domain.com`

To delete a configuration and restart Nginx using the Bash script, use the following command:

`sudo bash nginxconf.sh -d domain.com -r`

## License

This script is licensed under the [MIT License](LICENSE).
