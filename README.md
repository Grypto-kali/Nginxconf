# Nginxconf and rm_nginxconf

This script (nginxconf.py) is a Python script that automates the process of creating directories, configuring Nginx server settings, and creating symbolic links for domain and subdomain setups.

When you run the script, it will prompt you to enter a file name representing the domain or subdomain name you want to create.

If you enter a main domain name like gryptokali.com, the script will create the necessary directories and configuration files specific to that main domain. It will create the log directory at /var/log/nginx/gryptokali.com/, the web directory at /var/www/gryptokali.com/, and the Nginx configuration file at /etc/nginx/sites-available/gryptokali.com. Additionally, a symbolic link will be created in /etc/nginx/sites-enabled/ to enable the site.

However, if you enter a subdomain like test.gryptokali.com, the script will first check if the main domain directory (/var/www/gryptokali.com/) exists. If it does, the script will proceed to create the necessary subdomain directories and configuration files specific to that subdomain. It will create the log directory at /var/log/nginx/gryptokali.com/test.gryptokali.com/ and the web directory at /var/www/gryptokali.com/test.gryptokali.com/. The Nginx configuration file will be created at /etc/nginx/sites-available/test.gryptokali.com, and a symbolic link will be created in /etc/nginx/sites-enabled/ to enable the subdomain site.
