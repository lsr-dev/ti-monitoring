# Import packages
from mylibrary import *
from myconfig import *


def main():

    initialize_data_file(
        file_name
    )

    # -------------------------------------------------
    # CIS monitoring data
    # -------------------------------------------------

    current_data = update_cis(
        file_name,
        url,
    )

    # -------------------------------------------------
    # TI application status
    # -------------------------------------------------

    app_status = update_apps(
        file_name,
        app_status_url,
    )

    # -------------------------------------------------
    # Current-state cache
    # -------------------------------------------------

    write_data_cache(
        {
            "cis": current_data.to_dict(
                orient="records"
            ),
            "app_status": app_status,
        }
    )

    # -------------------------------------------------
    # Notifications
    # -------------------------------------------------

    if notifications:
        send_notifications(
            file_name,
            notifications_config_file,
            smtp_settings,
            home_url,
        )

    if push_notifications:
        send_push_notifications(
            file_name,
            notifications_config_file,
            home_url,
            ntfy_url,
            ntfy_token,
        )


if __name__ == '__main__':
    main()
