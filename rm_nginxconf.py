import os
import shutil

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

def main():
    file_name = input("Enter the file name: ")

    parts = file_name.split(".")
    if len(parts) == 2:
        subdomain = ""
        domain = file_name
    else:
        subdomain = parts[0]
        domain = ".".join(parts[1:])

    log_dir = os.path.join("/var/log/nginx/", domain, file_name)
    www_dir = os.path.join("/var/www/", domain, file_name)
    nginx_dir = os.path.join("/etc/nginx/sites-available/", file_name)
    nginx_link = os.path.join("/etc/nginx/sites-enabled/", file_name)

    delete_file(log_dir)
    delete_file(www_dir)
    delete_file(nginx_dir)
    delete_file(nginx_link)

if __name__ == "__main__":
    main()
