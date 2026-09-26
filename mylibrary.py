# Import packages
import numpy as np
import pandas as pd
import h5py as h5
import requests, json, time, pytz, os
from datetime import datetime, timezone
from tzlocal import get_localzone
import tempfile
import smtplib
from email.message import EmailMessage
from email.mime.text import MIMEText

DATA_CACHE_FILE = os.getenv(
    "DATA_CACHE_FILE",
    "data_cache.json",
)

def initialize_data_file(file_name):
    """
    Creates HDF5 file if necessary and builds up basic
    group structure.

    Args:
        file_name (str): Path to HDF5 file.

    Returns:
        None
    """

    if not os.path.isfile(file_name):
        with h5.File(file_name, "w") as f:
            f.create_group("availability")
            f.create_group("configuration_items")
            f.create_group("app_status")

def update_cis(file_name, url):
    response = requests.get(
        url,
        headers={
            "Accept": "application/json",
        },
        timeout=10,
    )

    response.raise_for_status()

    data = response.json()

    df = pd.DataFrame(data)

    current_data = []

    # -------------------------------------------------
    # HDF5 datatype for historical availability
    # -------------------------------------------------

    history_dtype = np.dtype([
        (
            "timestamp",
            "S32",
        ),
        (
            "availability",
            "i1",
        ),
    ])

    with h5.File(file_name, "a") as f:

        for idx in range(len(df)):

            ci = df.iloc[idx]

            ci_id = str(
                ci["ci"]
            )

            # -------------------------------------------------
            # Timestamp
            # -------------------------------------------------

            timestamp = str(
                ci["time"]
            )

            # -------------------------------------------------
            # Availability
            # -------------------------------------------------

            av = int(
                ci["availability"]
            )

            # -------------------------------------------------
            # Historical availability
            # -------------------------------------------------

            availability_group = (
                f.require_group(
                    "availability"
                )
            )

            ci_history_group = (
                availability_group.require_group(
                    ci_id
                )
            )

            if "history" not in ci_history_group:

                history = (
                    ci_history_group.create_dataset(
                        "history",
                        shape=(0,),
                        maxshape=(None,),
                        dtype=history_dtype,
                    )
                )

            else:

                history = (
                    ci_history_group["history"]
                )

            # -------------------------------------------------
            # Prevent duplicate timestamps
            # -------------------------------------------------

            duplicate = False

            if len(history) > 0:

                last_timestamp = (
                    history[-1]["timestamp"]
                )

                if isinstance(
                    last_timestamp,
                    bytes,
                ):
                    last_timestamp = (
                        last_timestamp.decode(
                            "utf-8"
                        )
                    )

                if last_timestamp == timestamp:
                    duplicate = True

            # -------------------------------------------------
            # Append historical value
            # -------------------------------------------------

            if not duplicate:

                old_length = len(history)

                history.resize(
                    old_length + 1,
                    axis=0,
                )

                history[old_length] = (
                    timestamp.encode("utf-8"),
                    av,
                )

            # -------------------------------------------------
            # Configuration item metadata
            # -------------------------------------------------

            group_ci = (
                f.require_group(
                    "configuration_items/"
                    + ci_id
                )
            )

            str_256 = h5.string_dtype(
                encoding="utf-8",
                length=256,
            )

            for property in [
                "tid",
                "bu",
                "organization",
                "pdt",
                "product",
                "name",
                "comment",
                "time",
            ]:

                ds = group_ci.require_dataset(
                    property,
                    shape=(),
                    dtype=str_256,
                )

                ds[()] = str(
                    ci[property]
                )

            # -------------------------------------------------
            # Availability difference
            # -------------------------------------------------

            if "current_availability" in group_ci:

                prev_av = int(
                    group_ci[
                        "current_availability"
                    ][()]
                )

                av_diff = (
                    av - prev_av
                )

            else:

                av_diff = 0

            ds = group_ci.require_dataset(
                "availability_difference",
                shape=(),
                dtype=int,
            )

            ds[()] = av_diff

            # -------------------------------------------------
            # Current availability
            # -------------------------------------------------

            ds = group_ci.require_dataset(
                "current_availability",
                shape=(),
                dtype=int,
            )

            ds[()] = av

            # -------------------------------------------------
            # Data returned to cron.py
            # -------------------------------------------------

            current_data.append(
                {
                    "ci": ci_id,
                    "tid": str(
                        ci["tid"]
                    ),
                    "bu": str(
                        ci["bu"]
                    ),
                    "organization": str(
                        ci["organization"]
                    ),
                    "pdt": str(
                        ci["pdt"]
                    ),
                    "product": str(
                        ci["product"]
                    ),
                    "name": str(
                        ci["name"]
                    ),
                    "comment": str(
                        ci["comment"]
                    ),
                    "time": timestamp,
                    "availability_difference": int(
                        av_diff
                    ),
                    "current_availability": av,
                }
            )

    return pd.DataFrame(
        current_data
    )

def update_apps(file_name, url):
    """
    Gets current TI application status from the API,
    updates the app_status HDF5 history and returns the
    current application status.

    Args:
        file_name: Path to the HDF5 file.
        url: URL of the TI Lage API.

    Returns:
        dict: Current TI application status.
    """

    response = requests.get(
        url,
        headers={
            "Accept": "application/json",
        },
        timeout=10,
    )

    response.raise_for_status()

    data = response.json()

    # -------------------------------------------------
    # Timestamp
    # -------------------------------------------------

    timestamp = data.get(
        "timestamp"
    )

    if timestamp is None:

        timestamp = datetime.now(
            timezone.utc
        ).isoformat()

    timestamp = str(
        timestamp
    )

    # -------------------------------------------------
    # Application status
    # -------------------------------------------------

    app_status = data.get(
        "appStatus",
        {}
    )

    # -------------------------------------------------
    # HDF5 datatype for application history
    # -------------------------------------------------

    history_dtype = np.dtype([
        (
            "timestamp",
            "S32",
        ),
        (
            "status",
            "S32",
        ),
    ])

    with h5.File(
        file_name,
        "a",
    ) as f:

        group = f.require_group(
            "app_status"
        )

        for app_name, app_data in app_status.items():

            # -------------------------------------------------
            # Application subgroup
            # -------------------------------------------------

            app_group = group.require_group(
                str(app_name)
            )

            # -------------------------------------------------
            # Current status
            # -------------------------------------------------

            status = app_data.get(
                "status"
            )

            if status is None:

                status = "unknown"

            status = str(
                status
            )

            # -------------------------------------------------
            # History dataset
            # -------------------------------------------------

            if "history" not in app_group:

                history = app_group.create_dataset(
                    "history",
                    shape=(0,),
                    maxshape=(None,),
                    dtype=history_dtype,
                )

            else:

                history = app_group[
                    "history"
                ]

            # -------------------------------------------------
            # Prevent duplicate timestamps
            # -------------------------------------------------

            duplicate = False

            if len(history) > 0:

                last_timestamp = (
                    history[-1]["timestamp"]
                )

                if isinstance(
                    last_timestamp,
                    bytes,
                ):

                    last_timestamp = (
                        last_timestamp.decode(
                            "utf-8"
                        )
                    )

                if last_timestamp == timestamp:

                    duplicate = True

            # -------------------------------------------------
            # Append new status
            # -------------------------------------------------

            if not duplicate:

                old_length = len(
                    history
                )

                history.resize(
                    old_length + 1,
                    axis=0,
                )

                history[old_length] = (
                    timestamp.encode(
                        "utf-8"
                    ),
                    status.encode(
                        "utf-8"
                    ),
                )

    return data

def read_data_cache():
    """
    Read the complete current-state cache.

    Returns an empty dictionary if the cache does not exist
    or contains invalid JSON.
    """

    try:
        with open(
            DATA_CACHE_FILE,
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)

    except (
        FileNotFoundError,
        json.JSONDecodeError,
        OSError,
    ):
        return {}

def write_data_cache(data):
    """
    Atomically write the complete current-state cache.
    """

    directory = os.path.dirname(
        os.path.abspath(DATA_CACHE_FILE)
    )

    fd, temporary_file = tempfile.mkstemp(
        dir=directory,
        prefix=".data_cache_",
        suffix=".tmp",
    )

    try:
        with os.fdopen(
            fd,
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=2,
            )

        os.replace(
            temporary_file,
            DATA_CACHE_FILE,
        )

    except Exception:
        try:
            os.unlink(temporary_file)
        except OSError:
            pass

        raise
        
def update_data_cache(section, data):
    """
    Update one section of the shared data cache.

    Example:
        update_data_cache("app_status", status_data)

    keeps the existing "cis" section intact.
    """

    cache = read_data_cache()

    cache[section] = data

    cache["cached_at"] = datetime.now(
        timezone.utc
    ).isoformat()

    write_data_cache(cache)

def get_availability_data_of_ci(
    file_name,
    ci,
):
    """
    Gets historical availability data of a CI.

    Args:
        file_name (str): Path to the HDF5 file.
        ci (str): Configuration item ID.

    Returns:
        DataFrame:
            Columns:
                - times
                - values
    """

    with h5.File(file_name, "r") as f:

        history = f[
            "availability/"
            + str(ci)
            + "/history"
        ]

        timestamps = history["timestamp"][:]
        values = history["availability"][:]

    # HDF5 strings may be returned as bytes.
    timestamps = [
        timestamp.decode("utf-8")
        if isinstance(timestamp, bytes)
        else timestamp
        for timestamp in timestamps
    ]

    times = pd.to_datetime(
        timestamps,
        utc=True,
    ).tz_convert(
        get_localzone()
    )

    return pd.DataFrame(
        {
            "times": times,
            "values": values,
        }
    )

def get_data_of_all_cis(file_name):
    """
    Gets general data for all configuration items from
    the HDF5 file, such as organization, product,
    current availability and availability difference.

    Args:
        file_name (str): Path to HDF5 file.

    Returns:
        DataFrame: Basic information about all
        configuration items.
    """

    all_ci_data = []

    with h5.File(file_name, "r") as f:

        configuration_items = f[
            "configuration_items"
        ]

        for ci in configuration_items:

            ci_group = configuration_items[ci]

            ci_data = {
                "ci": ci
            }

            for name in ci_group:

                dataset = ci_group[name]

                # Only read scalar datasets.
                if not isinstance(
                    dataset,
                    h5.Dataset,
                ):
                    continue

                value = dataset[()]

                if isinstance(
                    value,
                    bytes,
                ):
                    value = value.decode(
                        "utf-8"
                    )

                ci_data[name] = value

            all_ci_data.append(
                ci_data
            )

    return pd.DataFrame(
        all_ci_data
    )

def get_data_of_ci(file_name, ci):
    """
    Gets general data for a specific configuration
    item from the HDF5 file.

    Args:
        file_name (str): Path to HDF5 file.
        ci (str): ID of the desired configuration item.

    Returns:
        dict: General data of the desired
        configuration item.
    """

    with h5.File(file_name, "r") as f:

        ci_group = f[
            "configuration_items/"
            + str(ci)
        ]

        ci_data = {
            "ci": str(ci)
        }

        for name in ci_group:

            dataset = ci_group[name]

            # Only read scalar datasets.
            if not isinstance(
                dataset,
                h5.Dataset,
            ):
                continue

            value = dataset[()]

            if isinstance(
                value,
                bytes,
            ):
                value = value.decode(
                    "utf-8"
                )

            ci_data[name] = value

    return ci_data

def pretty_timestamp(timestamp_str):
    """
    Converts UTC timestamp of API to pretty formatted timestamp in local time

    Args:
        timestamp_str (str): UTC timestamp from API

    Returns:
        str: pretty formatted timestamp in local time
    """
    utc_time = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%S.%fZ')
    utc_time = utc_time.replace(tzinfo=pytz.UTC)
    berlin_time = utc_time.astimezone(pytz.timezone('Europe/Berlin'))
    formatted_time = berlin_time.strftime('%d.%m.%Y %H:%M:%S Uhr')
    return formatted_time

def send_mail(smtp_settings, recipients, subject, html_message):
    """
    Sends a html-formatted mail to a specified reciepient using SMTP

    Args:
        smtp_settings (dict): host, port, username, password and sender address (from)
        recipients (list of str): list of email addresses
        subject (str): mail subject
        html_message (str): html content of mail

    Returns:
        None
    """
    msg = EmailMessage()
    msg.add_alternative(html_message, subtype='html')
    msg['Subject'] = subject
    msg['From'] = smtp_settings['from']
    msg['Bcc'] = recipients
    s = smtplib.SMTP(
        host = smtp_settings['host'],
        port = smtp_settings['port']
    )
    s.ehlo()
    s.starttls()
    s.login(
        user = smtp_settings['user'],
        password = smtp_settings['password']
    )
    s.send_message(msg)
    s.quit()

def create_html_list_item_for_change(change, home_url):
    """
    Creates a html list item element for a configuration item with changed availability status

    Args:
        change (DataFrame): data for an individual configuration item containing information
        such as organization and product as well as current availability and availability difference
        home_url (str): base url of dash app

    Returns:
        str: html list item element
    """
    if home_url:
        href = home_url + '/plot?ci=' + str(change['ci'])
    else:
        href = ''
    html_str = '<li><strong><a href="' + href + '">' + str(change['ci']) + '</a></strong>: ' + str(change['product']) + ', ' + str(change['name']) + ', ' + str(change['organization']) + ' '
    if change['availability_difference'] == 1:
        html_str += '<span style=color:green>ist wieder verfügbar</span>'
    elif change['availability_difference'] == -1:
        html_str += '<span style=color:red>ist nicht mehr verfügbar</span>'
    else:
        html_str += 'keine Veränderung'
    html_str += ', Stand: ' + str(pretty_timestamp(change['time'])) + '</li>'
    return html_str

def send_notifications(file_name, notifications_config_file, smtp_settings, home_url):
    """
    Sends email notifications for each notification configuration about all
    changes that are relevant for the respective configuration

    Args:
        file_name (str): Path to hdf5 file
        notifications_config_file (str): Path to json file with notification configurations
        smtp_settings (dict): host, port, username, password and sender address (from)
        home_url (str): base url of dash app

    Returns:
        None
    """
    # get notification config
    with open(notifications_config_file, 'r', encoding='utf-8') as f:
        notification_config = json.load(f)
    # get changes 
    ci_data = get_data_of_all_cis(file_name)
    changes = ci_data[ci_data['availability_difference']!=0]
    changes_sorted = changes.sort_values(by = 'availability_difference')
    # filter relevant changes for each config and send mails
    for config in notification_config:
        try:
            if (config['type'] == 'whitelist'):
                relevant_changes = changes_sorted[changes_sorted['ci'].isin(config['ci_list'])]
            elif (config['type'] == 'blacklist'):
                relevant_changes = changes_sorted[~changes_sorted['ci'].isin(config['ci_list'])]
            number_of_relevant_changes = len(relevant_changes)
            if number_of_relevant_changes > 0:
                message = '<html lang="de"><body><p>Hallo ' + str(config['name']) + ',</p>'
                message += '<p>bei der letzten Überprüfung hat sich die Verfügbarkeit der folgenden von Ihnen abonierten Komponenten geändert:</p><ul>'
                for index, change in relevant_changes.iterrows():
                    message += create_html_list_item_for_change(change, home_url)
                if home_url:    
                    message += '</ul><p>Den aktuellen Status aller Komponenten können Sie unter <a href="' + home_url + '">' + home_url + '</a> einsehen.</p>'
                message += '<p>Weitere Hintergrundinformationen finden Sie im <a href="https://fachportal.gematik.de/ti-status">Fachportal der gematik GmbH</a>.</p><p>Viele Grüße<br>TI-Monitoring</p></body></html>'
                subject = 'TI-Monitoring: ' + str(number_of_relevant_changes) + ' Änderungen der Verfügbarkeit'
                recipients = config['recipients']
                send_mail(smtp_settings, recipients, subject, message)
        except:
            print('Sending notification for profile failed. Please check notifications config file.')
            pass

def create_markdown_list_item_for_change(change):
    """
    Creates a markdown list item element for a configuration item with changed availability status

    Args:
        change (DataFrame): data for an individual configuration item containing information
        such as organization and product as well as current availability and availability difference

    Returns:
        str: html list item element
    """
    if change['availability_difference'] == 1:
        md_str = '🟢 '
    elif change['availability_difference'] == -1:
        md_str = '🔴 '
    else:
        md_str = '⚫️ '
    md_str += str(change['ci']) + ': ' + str(change['product']) + ', ' + str(change['name']) + ', ' + str(change['organization']) + ' '
    if change['availability_difference'] == 1:
        md_str += 'ist wieder verfügbar'
    elif change['availability_difference'] == -1:
        md_str += 'ist nicht mehr verfügbar'
    else:
        md_str += 'keine Veränderung'
    md_str += ', Stand: ' + str(pretty_timestamp(change['time'])) + '\n'
    return md_str

def send_push_notifications(file_name, notifications_config_file, home_url, ntfy_url, ntfy_token):
    """
    Sends push notifications for each notification configuration about all
    changes that are relevant for the respective configuration

    Args:
        file_name (str): Path to hdf5 file
        notifications_config_file (str): Path to json file with notification configurations
        home_url (str): base url of dash app
        ntfy_url (str): base url for push notifications
        ntfy_token (str): access token for push notifications

    Returns:
        None
    """
    # get notification config
    with open(notifications_config_file, 'r', encoding='utf-8') as f:
        notification_config = json.load(f)
    # get changes 
    ci_data = get_data_of_all_cis(file_name)
    changes = ci_data[ci_data['availability_difference']!=0]
    changes_sorted = changes.sort_values(by = 'availability_difference')
    # filter relevant changes for each config and send mails
    for config in notification_config:
        if (config['push_topic'] != ''):
            try:
                if (config['type'] == 'whitelist'):
                    relevant_changes = changes_sorted[changes_sorted['ci'].isin(config['ci_list'])]
                elif (config['type'] == 'blacklist'):
                    relevant_changes = changes_sorted[~changes_sorted['ci'].isin(config['ci_list'])]
                number_of_relevant_changes = len(relevant_changes)
                if number_of_relevant_changes > 0:
                    message = ""
                    for index, change in relevant_changes.iterrows():
                        message += create_markdown_list_item_for_change(change)
                    subject = str(number_of_relevant_changes) + ' Änderung(en) der Verfügbarkeit'
                    ntfy_topic_url = ntfy_url + '/' + config['push_topic']
                    requests.post(ntfy_topic_url,
                        data=message.encode(encoding='utf-8'),
                        headers={
                            "title": subject.encode(encoding='utf-8'),
                            "markdown": "yes",
                            "authorization": "Bearer " + ntfy_token,
                            "actions": f"view, Übersicht, {home_url}; view, Alerts, {ntfy_topic_url}; view, Fachportal, https://fachportal.gematik.de/ti-status".encode(encoding='utf-8')
                        }
                    )
            except:
                print('Sending push notification for profile failed. Please check notifications config file.')
                pass

def main():
    return

if __name__ == '__main__':
    main()