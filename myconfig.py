# URL for API
url = "https://ti-lage.prod.ccs.gematik.solutions/lageapi/v1/tilage/bu/PU"

# path to hdf5 file for saving the availability data 
file_name = "data.hdf5"

# switching email notofications on/off
notifications = False

# configuration for notofications
notifications_config_file = 'notifications.json'

# smtp settings for email notifications
smtp_settings = {
    'host' : '********',
    'port' : 587,
    'user' : '********',
    'password' : '********',
    'from' : '********'
}

# home url for dash app
home_url = 'https://ti-monitoring.de'

# time frame for statistics in web app
stats_delta_hours = 12

# switching push notofications on/off
push_notifications = False

# base url for push notifications
ntfy_url = 'https://push.ti-monitoring.de'

# access token for push notifications
ntfy_token = '********'

def main():
    return

if __name__ == '__main__':
    main()