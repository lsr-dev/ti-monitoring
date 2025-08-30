import os

# Config through environment variables
URL_ENV = "TI_MONITORING_URL"
FILE_NAME_ENV = "TI_MONITORING_FILE_NAME"
NOTIFICATIONS_ENV = "TI_MONITORING_NOTIFICATIONS"
NOTIFICATIONS_CONFIG_FILE_ENV = "TI_MONITORING_NOTIFICATIONS_CONFIG_FILE"
SMTP_HOST_ENV = "TI_MONITORING_SMTP_HOST"
SMTP_PORT_ENV = "TI_MONITORING_SMTP_PORT"
SMTP_USER_ENV = "TI_MONITORING_SMTP_USER"
SMTP_PASSWORD_ENV = "TI_MONITORING_SMTP_PASSWORD"
SMTP_FROM_ENV = "TI_MONITORING_SMTP_FROM"
HOME_URL_ENV = "TI_MONITORING_HOME_URL"
STATS_DELTA_HOURS_ENV = "TI_MONITORING_STATS_DELTA_HOURS"

# Defaults when environment variables are not set
URL_DEFAULT = "https://ti-lage.prod.ccs.gematik.solutions/lageapi/v1/tilage/bu/PU"
FILE_NAME_DEFAULT = "data.hdf5"
NOTIFICATIONS_DEFAULT = "False"
NOTIFICATIONS_CONFIG_FILE_DEFAULT = "notifications.json"
SMTP_HOST_DEFAULT = "********"
SMTP_PORT_DEFAULT = "587"
SMTP_USER_DEFAULT = "********"
SMTP_PASSWORD_DEFAULT = "********"
SMTP_FROM_DEFAULT = "********"
HOME_URL_DEFAULT = "https://ti-monitoring.lukas-schmidt-russnak.de"
STATS_DELTA_HOURS_DEFAULT = "12"

# URL for API
url = os.getenv(URL_ENV, URL_DEFAULT)

# path to hdf5 file for saving the availability data
file_name = os.getenv(FILE_NAME_ENV, FILE_NAME_DEFAULT)

# switching email notofications on/off
notifications = os.getenv(NOTIFICATIONS_ENV, NOTIFICATIONS_DEFAULT) == "True"

# configuration for notofications
notifications_config_file = os.getenv(NOTIFICATIONS_CONFIG_FILE_ENV, NOTIFICATIONS_CONFIG_FILE_DEFAULT)

# smtp settings for email notifications
smtp_settings = {
    'host' : os.getenv(SMTP_HOST_ENV, SMTP_HOST_DEFAULT),
    'port' : int(os.getenv(SMTP_PORT_ENV, SMTP_PORT_DEFAULT)),
    'user' : os.getenv(SMTP_USER_ENV, SMTP_USER_DEFAULT),
    'password' : os.getenv(SMTP_PASSWORD_ENV, SMTP_PASSWORD_DEFAULT),
    'from' : os.getenv(SMTP_FROM_ENV, SMTP_FROM_DEFAULT)
}

# home url for dash app
home_url = os.getenv(HOME_URL_ENV, HOME_URL_DEFAULT)

# time frame for statistics in web app
stats_delta_hours = int(os.getenv(STATS_DELTA_HOURS_ENV, STATS_DELTA_HOURS_DEFAULT))

def main():
    return

if __name__ == '__main__':
    main()