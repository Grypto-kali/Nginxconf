import os

# Ask the user for the file name (e.g., "test.gryptokali.com")
file_name = input("Enter the file name: ")

# Split the file name into subdomain and domain
parts = file_name.split(".")
if len(parts) == 2:
    subdomain = ""
    domain = file_name
else:
    subdomain = parts[0]
    domain = ".".join(parts[1:])

# Check if the main domain exists
if subdomain != "" and not os.path.exists(f"/var/www/{domain}"):
    print("The main domain does not exist. Please create the main domain before creating the subdomain.")
    exit()

# Create paths for directories
log_dir = os.path.join("/var/log/nginx/", domain, file_name)
www_dir = os.path.join("/var/www/", domain, file_name)

# Create directories if they don't already exist
os.makedirs(log_dir, exist_ok=True)
os.makedirs(www_dir, exist_ok=True)

# Create a file in /etc/nginx/sites-available/ with the given file name
nginx_dir = os.path.join("/etc/nginx/sites-available/", file_name)
with open(nginx_dir, "w") as f:
    f.write(f"server {{\n\n")
    f.write(f"\troot /var/www/{domain}/{file_name};\n")
    f.write(f"\tindex index.html index.htm index.nginx-debian.html;\n\n")
    f.write(f"\tserver_name {file_name};\n\n")
    f.write(f"\tlocation / {{\n")
    f.write(f"\t\ttry_files $uri $uri/ =404;\n")
    f.write(f"\t}}\n\n")
    f.write(f"\taccess_log /var/log/nginx/{domain}/{file_name}/access.log;\n")
    f.write(f"\terror_log /var/log/nginx/{domain}/{file_name}/error.log;\n")
    f.write(f"}}\n")

# Create a symbolic link to the file in /etc/nginx/sites-enabled/
os.symlink(nginx_dir, f"/etc/nginx/sites-enabled/{file_name}")

print(f"Directories {log_dir} and {www_dir}, as well as the file {nginx_dir}, have been created. Symbolic link created in /etc/nginx/sites-enabled/")
