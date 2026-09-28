#!/usr/bin/env bash

set -euo pipefail

PHP_FPM_SOCKET="unix:/var/run/php/php8.1-fpm.sock"

parse_domain_parts() {
    local domain_input="$1"
    
    # Remove leading/trailing spaces
    domain_input="$(echo "$domain_input" | xargs)"
    
    IFS='.' read -r -a parts <<< "$domain_input"
    
    if [ "${#parts[@]}" -lt 2 ]; then
        echo "Error: Invalid domain format. Expected domain.tld or sub.domain.tld" >&2
        exit 1
    fi

    if [ "${#parts[@]}" -eq 2 ]; then
        subdomain=""
        domain="$domain_input"
    else
        subdomain="${parts[0]}"
        domain="${domain_input#*.}"
    fi
}

add_configuration() {
    local file_name="$1"
    local subdomain=""
    local domain=""
    
    parse_domain_parts "$file_name"

    if [ -n "$subdomain" ] && [ ! -d "/var/www/$domain" ]; then
        echo "Error: Main domain '/var/www/$domain' does not exist. Please create the main domain before creating the subdomain." >&2
        exit 1
    fi

    local log_dir="/var/log/nginx/$domain/$file_name"
    local www_dir="/var/www/$domain/$file_name"
    local nginx_available="/etc/nginx/sites-available/$file_name"
    local nginx_enabled="/etc/nginx/sites-enabled/$file_name"

    mkdir -p "$log_dir" "$www_dir"

    cat <<EOL > "$nginx_available"
server {
    listen 80;
    server_name $file_name;

    root $www_dir;
    index index.html index.htm index.nginx-debian.html index.php;

    location / {
        try_files \$uri \$uri/ =404;
    }

    location ~ \\.php\$ {
        include snippets/fastcgi-php.conf;
        fastcgi_pass $PHP_FPM_SOCKET;
    }

    location ~ /\\.ht {
        deny all;
    }

    access_log $log_dir/access.log;
    error_log $log_dir/error.log;
}
EOL

    # Force creation of symlink (-sf) to overwrite existing symlinks safely
    ln -sf "$nginx_available" "$nginx_enabled"
    echo "Adding Nginx configuration for $file_name"
}

delete_file() {
    local file_path="$1"
    
    if [ -L "$file_path" ]; then
        rm -f "$file_path"
        echo "Symlink $file_path was successfully deleted."
    elif [ -d "$file_path" ]; then
        rm -rf "$file_path"
        echo "Directory $file_path was successfully deleted."
    elif [ -f "$file_path" ]; then
        rm -f "$file_path"
        echo "File $file_path was successfully deleted."
    fi
}

delete_configuration() {
    local file_name="$1"
    local subdomain=""
    local domain=""
    
    parse_domain_parts "$file_name"

    if [ -z "$subdomain" ] && [ -d "/var/www/$domain" ]; then
        # Find subdirectories safely, excluding empty matches
        shopt -s nullglob
        local subdirectories=(/var/www/$domain/*)
        shopt -u nullglob

        local subdomains=()
        for sub_path in "${subdirectories[@]}"; do
            if [ -d "$sub_path" ]; then
                local sub_name
                sub_name=$(basename "$sub_path")
                if [ "$sub_name" != "$domain" ]; then
                    subdomains+=("$sub_name")
                fi
            fi
        done

        if [ ${#subdomains[@]} -gt 0 ]; then
            echo "Warning: Deleting the main domain '$domain' will also delete the subdomains: ${subdomains[*]}"
            read -r -p "Are you sure you want to proceed? (yes/no): " confirmation
            if [ "$confirmation" != "yes" ]; then
                echo "Aborting deletion."
                exit 1
            fi

            for sub in "${subdomains[@]}"; do
                delete_configuration "$sub"
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

reload_nginx() {
    for arg in "$@"; do
        if [ "$arg" == "-r" ]; then
            echo "Testing Nginx configuration..."
            if sudo nginx -t; then
                sudo systemctl reload nginx
                echo "Nginx reloaded successfully."
            else
                echo "Error: Nginx syntax test failed. Service not reloaded." >&2
                exit 1
            fi
            break
        fi
    done
}

main() {
    if [ $# -lt 2 ] || [[ ! "$1" =~ ^-(a|d)$ ]]; then
        echo "Usage: bash nginxconf.sh [-a/-d] domain.com [-r]"
        exit 1
    fi

    local action="$1"
    local file_name="$2"

    if [ "$action" == "-a" ]; then
        add_configuration "$file_name"
    elif [ "$action" == "-d" ]; then
        delete_configuration "$file_name"
    fi

    reload_nginx "$@"
}

main "$@"
