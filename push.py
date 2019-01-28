import onesignal as onesignal_sdk

def add_device(client, email, type, account, push_notifications):
    device_body = {
        'type': type,
        'accountType': account,
        'email': email,
        'language': 'en'
    }
    response = client.create_device(device_body=device_body)
    if response['success']:
        user = {
            'email': email,
            'pushID': response['id']
        }
        push_notifications.insert_one(user)
        return True
    else:
        return False

def send_notification(client, email, notification, heading, push_notifications):
    new_notification = onesignal_sdk.Notification(contents= {"en": notification})
    new_notification.set_parameter("headings", {"en": heading})
    user = push_notifications.find_one({'email': email})
    id = user['pushID']
    new_notification.set_target_devices([id])
    response = client.send_notification(new_notification)
    if response.status_code == 200:
        return True
    return False
