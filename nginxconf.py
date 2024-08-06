#!/usr/bin/env python3

import os
import shutil
import subprocess
import sys

def add_configuration(file_name):
    parts = file_name.split(".")
    if len(parts) == 2:
        subdomain = ""
        domain = file_name
    else:
        subdomain = parts[0]
        domain = ".".join(parts[1:])

    if subdomain != "" and not os.path.exists(f"/var/www/{domain}"):
        print("The main domain does not exist. Please create the main domain before creating the subdomain.")
        sys.exit(1)

    log_dir = os.path.join("/var/log/nginx/", domain, file_name)
    www_dir = os.path.join("/var/www/", domain, file_name)

    os.makedirs(log_dir, exist_ok=True)
    os.makedirs(www_dir, exist_ok=True)

    nginx_dir = os.path.join("/etc/nginx/sites-available/", file_name)
    with open(nginx_dir, "w") as f:
        f.write(f"server {{\n")
        f.write(f"\troot /var/www/{domain}/{file_name};\n")
        f.write(f"\tindex index.html index.htm index.nginx-debian.html index.php;\n\n")
        f.write(f"\tserver_name {file_name};\n\n")
        
        # PHP location block
        f.write(f"\tlocation / {{\n")
        f.write(f"\t\ttry_files $uri $uri/ =404;\n")
        f.write(f"\t}}\n\n")
        
        f.write(f"\tlocation ~ \\.php$ {{\n")
        f.write(f"\t\tinclude snippets/fastcgi-php.conf;\n")
        f.write(f"\t\tfastcgi_pass unix:/var/run/php/php8.1-fpm.sock;\n") # Adjust PHP version as needed
        f.write(f"\t}}\n\n")
        
        f.write(f"\tlocation ~ /\\.ht {{\n")
        f.write(f"\t\tdeny all;\n")
        f.write(f"\t}}\n\n")

        f.write(f"\taccess_log /var/log/nginx/{domain}/{file_name}/access.log;\n")
        f.write(f"\terror_log /var/log/nginx/{domain}/{file_name}/error.log;\n")
        f.write(f"}}\n")

    os.symlink(nginx_dir, f"/etc/nginx/sites-enabled/{file_name}")
    print(f"Adding Nginx configuration for {file_name}")

def restart_nginx():
    if "-r" in sys.argv:
        os.system("sudo systemctl restart nginx")
        print("Nginx restarted.")
        
def delete_file(file_path):
    try:
        if os.path.isdir(file_path):
            shutil.rmtree(file_path)
            print(f"Directory {file_path} was successfully deleted.")
        else:
            os.remove(file_path)
            print(f"File {file_path} was successfully deleted.")
    except FileNotFoundError:
        print(f"File or directory {file_path} not found.")
    except PermissionError:
        print(f"Insufficient permissions to delete file or directory {file_path}.")
    except Exception as e:
        print(f"An error occurred while deleting file or directory {file_path}: {str(e)}")
    
def delete_configuration(file_name):
    parts = file_name.split(".")
    if len(parts) == 2:
        subdomain = ""
        domain = file_name
    else:
        subdomain = parts[0]
        domain = ".".join(parts[1:])

    if subdomain == "":
        subdomains = [f for f in os.listdir(f"/var/www/{domain}") if os.path.isdir(os.path.join(f"/var/www/{domain}", f))]
        
        if subdomains:
            print(f"Warning: Deleting the main domain '{domain}' will also delete the subdomains:")
            confirmation = input("Are you sure you want to proceed? (yes/no): ").lower()
            
            if confirmation != "yes":
                print("Aborting deletion.")
                sys.exit(1)

            for sub in subdomains:
                delete_configuration(f"{sub}.{domain}")

        delete_file(os.path.join("/var/www/", domain))
        delete_file(os.path.join("/var/log/nginx/", domain))

    log_dir = os.path.join("/var/log/nginx/", domain, file_name)
    www_dir = os.path.join("/var/www/", domain, file_name)
    nginx_dir = os.path.join("/etc/nginx/sites-available/", file_name)
    nginx_link = os.path.join("/etc/nginx/sites-enabled/", file_name)

    delete_file(log_dir)
    delete_file(www_dir)
    delete_file(nginx_dir)
    delete_file(nginx_link)

    print(f"Nginx configuration for {file_name} deleted.")
    
def main():
    if len(sys.argv) < 3 or sys.argv[1] not in ['-a', '-d']:
        print("Usage: python3 nginxconf.py [-a/-d] domain.com [-r]")
        sys.exit(1)

    action = sys.argv[1]
    file_name = sys.argv[2]  

    if action == '-a':
        add_configuration(file_name)
    elif action == '-d':
        delete_configuration(file_name)
    else:
        print(f"Invalid action: {action}")
        
    restart_nginx()

if __name__ == "__main__":
    main()
