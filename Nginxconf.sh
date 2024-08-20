#!/bin/bash

function add_configuration {
    local file_name="$1"
    IFS='.' read -r -a parts <<< "$file_name"
    
    if [ ${#parts[@]} -eq 2 ]; then
        subdomain=""
        domain="$file_name"
    else
        subdomain="${parts[0]}"
        domain="${file_name#*.}"
    fi

    if [ ! -z "$subdomain" ] && [ ! -d "/var/www/$domain" ]; then
        echo "The main domain does not exist. Please create the main domain before creating the subdomain."
        exit 1
    fi

    local log_dir="/var/log/nginx/$domain/$file_name"
    local www_dir="/var/www/$domain/$file_name"
    local nginx_dir="/etc/nginx/sites-available/$file_name"

    mkdir -p "$log_dir" "$www_dir"

    cat <<EOL > "$nginx_dir"
server {
    root /var/www/$domain/$file_name;
    index index.html index.htm index.nginx-debian.html index.php;

    server_name $file_name;

    location / {
        try_files \$uri \$uri/ =404;
    }

    location ~ \\.php\$ {
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:/var/run/php/php8.1-fpm.sock;
    }

    location ~ /\\.ht {
        deny all;
    }

    access_log /var/log/nginx/$domain/$file_name/access.log;
    error_log /var/log/nginx/$domain/$file_name/error.log;
}
EOL

    ln -s "$nginx_dir" "/etc/nginx/sites-enabled/$file_name"
    echo "Adding Nginx configuration for $file_name"
}

function delete_file {
    local file_path="$1"
    if [ -d "$file_path" ]; then
        rm -rf "$file_path"
        echo "Directory $file_path was successfully deleted."
    else
        rm -f "$file_path"
        echo "File $file_path was successfully deleted."
    fi
}

function delete_configuration {
    local file_name="$1"
    IFS='.' read -r -a parts <<< "$file_name"

    if [ ${#parts[@]} -eq 2 ]; then
        subdomain=""
        domain="$file_name"
    else
        subdomain="${parts[0]}"
        domain="${file_name#*.}"
    fi

    if [ -z "$subdomain" ]; then
        local subdomains=(/var/www/$domain/*)
        if [ ${#subdomains[@]} -gt 0 ]; then
            echo "Warning: Deleting the main domain '$domain' will also delete the subdomains:"
            read -p "Are you sure you want to proceed? (yes/no): " confirmation
            if [ "$confirmation" != "yes" ]; then
                echo "Aborting deletion."
                exit 1
            fi
            for sub in "${subdomains[@]}"; do
                delete_configuration "$(basename "$sub").$domain"
            done
        fi
        delete_file "/var/www/$domain"
        delete_file "/var/log/nginx/$domain"
    fi

    delete_file "/var/log/nginx/$domain/$file_name"
    delete_file "/var/www/$domain/$file_name"
    delete_file "/etc/nginx/sites-available/$file_name"
    delete_file "/etc/nginx/sites-enabled/$file_name"

    echo "Nginx configuration for $file_name deleted."
}

function restart_nginx {
    if [[ " $@ " =~ " -r " ]]; then
        sudo systemctl restart nginx
        echo "Nginx restarted."
    fi
}

if [ $# -lt 2 ] || [[ ! "$1" =~ ^-(a|d)$ ]]; then
    echo "Usage: bash nginxconf.sh [-a/-d] domain.com [-r]"
    exit 1
fi

action="$1"
file_name="$2"

if [ "$action" == "-a" ]; then
    add_configuration "$file_name"
elif [ "$action" == "-d" ]; then
    delete_configuration "$file_name"
else
    echo "Invalid action: $action"
fi

restart_nginx "$@"
