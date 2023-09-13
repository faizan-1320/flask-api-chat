from datetime import datetime, timedelta
def expire_otp():
    current_datetime = datetime.now()
    is_expire = current_datetime + timedelta(minutes=1)
    # timestamp = is_expire.timestamp()
    # rounded_timestamp = round(timestamp)
    # print(rounded_timestamp)
    return is_expire