from flask import Flask, request, jsonify

def findNotifications(email,notifications):
    all = notifications.find({'email':str.lower(email)},{'_id': False})
    send_list = []
    dictresponse = {}
    for noti in all:
        #if not noti[complete]:
        send_list.append(noti)
    quicksort(send_list)
    for i in range(len(send_list)):
        dictresponse[i]=send_list[i]
    print(dictresponse)
    response = jsonify(dictresponse)
    response.response_code=200
    return response

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
