import onesignal as onesignal_sdk
import datetime
from threading import Timer

onesignal_client = onesignal_sdk.Client(user_auth_key="MjhmY2U2ZWMtN2YyNy00MWRlLWI3ZmYtNGZmMDljMWM5MjM0",
                                        app={"app_auth_key": "MmVhODM2YjEtZjM4Mi00MzNjLWIxNmUtNjAwYzM2ZWYxNDZi", "app_id": "4e80c299-4fec-4279-bde3-3cdffbb24e1d"})

#Function to add new device to push notifications database, allowing backedn to send push notifications to device through oneSignal
def add_device(email, type, account, push_notifications):
    device_body = {
        'type': type,
        'accountType': account,
        'device_type': 0,
        'email': email,
        'language': 'en'
    }
    response = onesignal_client.create_device(device_body=device_body)
    response=response.json()
    print(response)
    # print(response.headers.get('Success'))
    if response['success']:
        user = {
            'email': email,
            'pushID': response['id']
        }
        push_notifications.insert_one(user)
        return (True, response['id'])
    else:
        return (False, response['errors'])

#General fucntion for sending different types of notifications to user with given email through OneSignal
def send_notification(email, notification, heading, push_notifications):
    new_notification = onesignal_sdk.Notification(contents= {"en": notification})
    new_notification.set_parameter("headings", {"en": heading})
    user = push_notifications.find_one({'email': email})
    id = user['pushID']
    new_notification.set_target_devices([id])
    response = onesignal_client.send_notification(new_notification)
    print(response.json())
    if response.status_code == 200:
        return True
    return False

# Function to check and notify users with tasks due within 24 hours; runs every hour using timer object from threading
def check_task_notis(tasks, push_notifications):
    now = datetime.datetime.now()
    incompleteTasks = tasks.find({'complete':False},{'_id': False})
    for task in incompleteTasks:
        if (now - task['taskDeadline'] <= datetime.timedelta(hours=24)) and (now - task['taskDeadline'] > datetime.timedelta(hours = 22.9)):
            notString = 'Your task ' + task['taskName'] + ' is due in les than 24 hours!'
            send_notification(task['childEail'], notString, 'Task Due Soon!', push_notifications)
    t = Timer(3600, check_task_notis)
    t.start()
