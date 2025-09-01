# Import packages
from mylibrary import *
from myconfig import *

def main():
    initialize_data_file(file_name)
    update_file(file_name, url)
    if notifications:
        send_notifications(file_name, notifications_config_file, smtp_settings, home_url)
    if push_notifications:
        send_push_notifications(file_name, notifications_config_file, home_url, ntfy_url, ntfy_token)

if __name__ == '__main__':
    main()