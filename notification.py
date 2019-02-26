from flask import Flask, request, jsonify
from handleEmail import *
import datetime

#Main worker function for searching and sorting within notifcations database for each user
def findNotifications(email,notifications):
    all = notifications.find({'email':str.lower(email)},{'_id': False})
    send_list = []
    dictresponse = {}
    now =datetime.datetime.now()

    for noti in all:
        if not noti['read']:
            if not (noti['notificationType'] == 'newTask'):
                send_list.append(noti)
            else:
                date_time_obj = datetime.datetime.strptime(noti['deadline'], '%b %d %Y %I:%M%p')
                if ((date_time_obj - now) > datetime.timedelta(minutes=0)):
                    if ((date_time_obj - now) < datetime.timedelta(hours=24)):
                        noti['displayRed'] = True
                    else:
                        noti['displayRed'] = False
                    send_list.append(noti)

    quicksort(send_list)
    for i in range(len(send_list)):
        dictresponse[i]=send_list[i]
    response = jsonify(dictresponse)
    response.status_code=200
    return response

def readNotifications(request, notifications):
    request_json = request.get_json()
    email = fixEmail(request_json['payLoad']['email'])
    priority = request_json['payLoad']['priority']
    notiList = notifications.find({'email':email})
    for notis in notiList:
        if notis['priority'] == priority:
            readNoti = notis
            break
    notifications.update_one({'_id': readNoti['_id']}, {"$set":{'read': True}},upsert = False)
    response = jsonify([{
    }])
    response.status_code = 200
    return response

#Helper function for sorting notifications by order of time raised
def partition(the_list, p, r):
    i = p - 1              # i demarcates the end of the sublist containing values <= pivot.
    j = p                  # j demarcates end of sublist containing values > pivot.
    pivot = the_list[r]['priority']    # Pivot will store value of sublist's last item.
    while j < r:
        if the_list[j]['priority'] < pivot:
            j += 1         # Increment j.
        elif the_list[j]['priority'] >= pivot:
            i += 1         # Increment i.
            the_list[i], the_list[j] = the_list[j], the_list[i]
            j += 1
    the_list[r], the_list[i + 1] = the_list[i + 1], the_list[r]
    return i + 1

# Sort the_list[p ... r], using quick sort.
def quicksort(the_list, p = 0, r = None):
    # If using the default parameters, sort the entire list.
    if r == None:
        r = len(the_list) - 1
    # Base case: If sublist has fewer than 2 items... then do nothing. No code required!
    if p < r:
        q = partition(the_list, p, r)  # Locates pivot item, since partition returns its index.
        quicksort(the_list, p, q - 1)  # Quicksort sublist from p to q (exclusive).
        quicksort(the_list, q + 1, r)  # Quicksort sublist from one past q to r (inclusive).
    return the_list
