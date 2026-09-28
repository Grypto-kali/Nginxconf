#!/usr/bin/env python3

import os
import shutil
import subprocess
import sys

PHP_FPM_SOCKET = "unix:/var/run/php/php8.1-fpm.sock"


def parse_domain_parts(domain_name: str):
    """Parses domain and subdomain components safely."""
    parts = domain_name.strip().split(".")
    if len(parts) < 2:
        print(
            "Error: Invalid domain format. Expected domain.tld or sub.domain.tld"
        )
        sys.exit(1)

    if len(parts) == 2:
        return "", domain_name
    
    subdomain = parts[0]
    base_domain = ".".join(parts[1:])
    return subdomain, base_domain


def add_configuration(domain_name: str):
    subdomain, base_domain = parse_domain_parts(domain_name)

    # Check if main domain directory exists when adding a subdomain
    if subdomain and not os.path.exists(f"/var/www/{base_domain}"):
        print(
            f"Error: Main domain '/var/www/{base_domain}' does not exist. Create it first."
        )
        sys.exit(1)

    log_dir = os.path.join("/var/log/nginx", base_domain, domain_name)
    www_dir = os.path.join("/var/www", base_domain, domain_name)

    os.makedirs(log_dir, exist_ok=True)
    os.makedirs(www_dir, exist_ok=True)

    nginx_available_path = os.path.join(
        "/etc/nginx/sites-available", domain_name
    )
    nginx_enabled_path = os.path.join("/etc/nginx/sites-enabled", domain_name)

    nginx_config = f"""server {{
    listen 80;
    server_name {domain_name};

    root {www_dir};
    index index.html index.htm index.nginx-debian.html index.php;

    location / {{
        try_files $uri $uri/ =404;
    }}

    location ~ \\.php$ {{
        include snippets/fastcgi-php.conf;
        fastcgi_pass {PHP_FPM_SOCKET};
    }}

    location ~ /\\.ht {{
        deny all;
    }}

    access_log {log_dir}/access.log;
    error_log {log_dir}/error.log;
}}
"""

    try:
        with open(nginx_available_path, "w") as f:
            f.write(nginx_config)
    except PermissionError:
        print(
            f"Permission denied: Unable to write to {nginx_available_path}. Run with sudo."
        )
        sys.exit(1)

    # Safely create symbolic link
    if os.path.exists(nginx_enabled_path) or os.path.islink(
        nginx_enabled_path
    ):
        os.remove(nginx_enabled_path)

    os.symlink(nginx_available_path, nginx_enabled_path)
    print(f"Successfully added Nginx configuration for {domain_name}")


def delete_file_or_dir(file_path: str):
    """Safely removes a file, directory, or symbolic link."""
    try:
        if os.path.islink(file_path):
            os.unlink(file_path)
            print(f"Symlink {file_path} removed.")
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
            print(f"Directory {file_path} removed.")
        elif os.path.isfile(file_path):
            os.remove(file_path)
            print(f"File {file_path} removed.")
    except FileNotFoundError:
        pass
    except PermissionError:
        print(f"Permission denied: Unable to delete {file_path}")
    except Exception as e:
        print(f"An error occurred while deleting {file_path}: {e}")


def delete_configuration(domain_name: str):
    subdomain, base_domain = parse_domain_parts(domain_name)

    base_www_dir = os.path.join("/var/www", base_domain)

    # Deleting a primary domain
    if not subdomain and os.path.exists(base_www_dir):
        subdomains = [
            d
            for d in os.listdir(base_www_dir)
            if os.path.isdir(os.path.join(base_www_dir, d))
            and d != domain_name
        ]

        if subdomains:
            print(
                f"Warning: Deleting '{domain_name}' will also remove subdomains: {', '.join(subdomains)}"
            )
            confirmation = (
                input("Are you sure you want to proceed? (yes/no): ")
                .strip()
                .lower()
            )

            if confirmation != "yes":
                print("Aborting deletion.")
                sys.exit(1)

            for sub in subdomains:
                delete_configuration(sub)

        # Delete base www and log directories for the domain
        delete_file_or_dir(base_www_dir)
        delete_file_or_dir(os.path.join("/var/log/nginx", base_domain))

    # Clean individual site entries
    log_dir = os.path.join("/var/log/nginx", base_domain, domain_name)
    www_dir = os.path.join("/var/www", base_domain, domain_name)
    nginx_available_path = os.path.join(
        "/etc/nginx/sites-available", domain_name
    )
    nginx_enabled_path = os.path.join("/etc/nginx/sites-enabled", domain_name)

    delete_file_or_dir(log_dir)
    delete_file_or_dir(www_dir)
    delete_file_or_dir(nginx_enabled_path)
    delete_file_or_dir(nginx_available_path)

    print(f"Nginx configuration for {domain_name} deleted.")


def reload_or_restart_nginx():
    if "-r" in sys.argv:
        # Test configuration validity before reloading
        test_res = subprocess.run(
            ["sudo", "nginx", "-t"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if test_res.returncode != 0:
            print("Nginx configuration test failed! Not restarting Nginx.")
            print(test_res.stderr.decode())
            sys.exit(1)

        # Use systemctl via subprocess instead of shell execution
        res = subprocess.run(["sudo", "systemctl", "reload", "nginx"])
        if res.returncode == 0:
            print("Nginx configuration reloaded successfully.")
        else:
            print("Failed to reload Nginx.")


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in ["-a", "-d"]:
        print("Usage: python3 nginxconf.py [-a/-d] domain.com [-r]")
        sys.exit(1)

    action = sys.argv[1]
    domain_name = sys.argv[2]

    if action == "-a":
        add_configuration(domain_name)
    elif action == "-d":
        delete_configuration(domain_name)

    reload_or_restart_nginx()


if __name__ == "__main__":
    main()
