# Teller Backend

### Most of functionality doccumentation on [Frontend](https://github.com/dartmouth-cs98/18f-tellr-frontend) readme like specified in scaffolding assignment

# Tellr

Organize and streamline task assignment and chores in your household while teaching your kids the value of money!

![Parent](https://github.com/dartmouth-cs98/18f-tellr-frontend/blob/master/Data%20Model%20and%20Sketches/19W-Tellr-Parent.png)
![Main](https://github.com/dartmouth-cs98/18f-tellr-frontend/blob/master/Data%20Model%20and%20Sketches/19W-Tellr-Main.png)
![Child](https://github.com/dartmouth-cs98/18f-tellr-frontend/blob/master/Data%20Model%20and%20Sketches/Tellr-19W-Child.png)

## Setup

### Initial setup using Homebrew:

Install Homebrew, npm, node, yarn

### Setup of Local Python Environment

1. `brew install python`
2. `python -m pip install --user virtualenv`
3. `python -m virtualenv env`
4. `source env/bin/activate`
5. `pip install -r requirements.txt`
6. `export SECRET='secret'`
7. `python main.py`

### Setup of Local MongoDB (Optional)

1. `brew install mongodb`
2. `mkdir -p /data/db`
3. `sudo chown -R `id -un` /data/db`
4. `mongod`

## Deployment

To run locally with a _local_ database (requires the setup of a local MongoDB), default port 27017, run:

`python main.py local`

The online database is currently hosted on Heroku.

To run the backend locally on the online database, run:

`python main.py`

MLab URI: `mongodb://heroku_sxklq0jf:fvegd2q34of2qn0j5jivm9b51b@ds227243.mlab.com:27243/heroku_sxklq0jf`

Heroku API URL: `https://tellr-dartmouth.herokuapp.com/api`.

Note that line 6 sets the authentication secret to the string of your choice, in this case 'secret', which is also currently used as the configuration variable on Heroku (secrets need to be the same in order to enable account login from either local or Heroku backend).

## Authors

Hanting Guo, Scott Magnuson, Emily Pitts, Jed Rosen

## Architecture and Code Structure Overview

This backend uses MongoDB, Pymongo, and Flask, and follows the REST architecture style. Each file is named according to the primary area of functionality it is responsible for. The structure and functions of the main files are outlined below:

###### main.py
`main.py` houses all the API endpoints for the backend and processes all POST and GET requests and calls the relevant function(s) associated with those requests. `main.py` also constructs the MongoDB instance and relevant collections used by each function call. Additionally, all global variables are also housed at the top of `main.py`, which contain information on database location and login credentials for the email and push notification servers. Each API endpoint in `main.py` also calls the token verification function in `authenticate.py` to ensure that all requests are authentic. If a token is invalid or expired, `main.py` immediately sends back a 401 response without calling any other functions.

###### authenticate.py
`authenticate.py` handles all authentication-related functions, including account creation, login, password change, forgotten passwords, logouts, and token verification. It writes to the user database (called `people`) during account creation and the credentials database during password-related functions. `authenticate.py` uses the bcrypt library to cryptographically store passwords, and the jwt library to decrypt and encrypt tokens. Finally, `authenticate.py` is also responsible for updating the device ID of any logged in/ logged out users for the purpose of push notifications.

###### goals.py
`goals.py` handles all goal-related functions, including goal creation, goal verification, goal redemption, money redemption, and fetch-goal functions. These functions write to the goals database as well as the user database to update user balances in the case of redemptions, and also updates earnings history accordingly for analytics. Additionally, `goals.py` also uses the datetime library to record when a goal was redeemed, and generates notifications for the relevant users upon certain actions that are written to the notifications database.

###### notification.py
`notifications.py` is a smaller file that searches through the notifications database for all unread notifications for a given user. It then sorts the notifications based on priority before returning a dictionary of all notifications to the requester.

###### push.py
`push.py` is also a smaller file that implements the one-signal push notification framework. It uses the push IDs and login status written and updated in `authenticate.py` to determine which device a user is currently logged into (if any - this is found in the push_notifications database collection). It then contains a helper function `send_notification` which is called by many other files when a push notification should be sent to a user.

###### social.py
`social.py` handles all social-related functions including friend requests, friend removals, and fetching social-related stats. The former two functions update the user collection people for their relevant actions, while the fetch stats functions processes a list of tasks completed by the user as well as a list of all total tasks to generate graph-ready statistics and data.

###### tasks.py
`tasks.py` handles all task-related functions, including task creation, completion, verification, and fetches. This file mainly works with the tasks collection but also updates the user database in order to update user balances and analytical stats. Tasks also generates notifications that are written into the notification database, and uses the datetime library in the creation and sorting of tasks.

###### users.py
`users.py` is a large file that contains all relevant functions and calculations needed for the analytics implementation of the app. Using multiple entries from the `people` database collection, `users.py` calculates earnings, spend, balance history, and other statistics and formats/returns them in graph-ready dictionaries. `users.py` is also responsible for some ancillary functions such as fetching children names and other parents. 

#### Tech Stack
We are using React Native for our frontend and mobile app and flask for our backend.

#### Data Objects and Methods

The following are the data objects and endpoints for each GET and POST request currently in use by the app.

##### /api/childtasks/\<email\>
Methods: GET

Returns list of tasks assigned to child with email \<email\> in the format of a dictionary keyed on integers (0, 1, ...) to a dictionary with the following values:

`{
  taskName,
  reward,
  taskDeadline,
  taskDescription,
  childEmail,
  senderEmail,
  childName,
  complete,
  verified,
  dateCompleted,
  familyName
}`

##### /api/parenttasks/\<familyName\>
Methods: GET

Returns list of tasks assigned to all children in given familyName \<familyName\> in the format of a dictionary keyed on integers (0, 1, ...) to a dictionary with the following values:

`{
  taskName,
  reward,
  taskDeadline,
  taskDescription,
  childEmail,
  senderEmail,
  childName,
  complete,
  verified,
  dateCompleted,
  familyName
}`

##### /api/tasks
Methods: POST

Post a new task to this address with a json file named payLoad and the following values in the dictionary:

`{
  taskName,
  reward,
  taskDeadline,
  taskDescription,
  childEmail,
  senderEmail
}`

##### /api/tasks/seecompleted
Methods: GET

Returns a dictionary sorted by taskdeadline keyed on integers (0 corresponding to earliest task, and so on) with values that are smaller dictionaries representing tasks that are identical in structure to other methods that return tasks.

##### /api/users
Methods: POST

Add new users to the database by posting to this address with a json file named payLoad and the following values in its dictionary:

`{
  firstName,
  lastName,
  email,
  password,
  familyName,
  accountType
}`

##### /api/history/\<email\>
Methods: GET

Returns a dictionary keyed on integers with values in chronologoical order of all balances in user history. Values specifically are a list with the balance as the first element, the string of the date of that balance in the second element, and a description of what caused the change in balance as the third element. TASK means a change due to verified task, RED means a change due to a money redemption, GOAL means a change due to a goal redemption.

##### /api/history/\<email\>/\<timeframe\>
Methods: GET

Returns the same dictionary as above but limited to the given timeframe. Input 'week' for history for past week, 'month' for history for past month, and 'year' for history of past year.

##### /api/analytics/\<email\>/\<timeframe\>
Methods: GET

Same inputs as timeframe as above. Returns a dictionary keyed on the following values:

`{
  tasksCompleted,
  goalsRedeemed,
  redemptions,
  moneyReeemed,
  task_earned,
  goal_used,
  redemptions,
  avgTask,
  avgGoal,
  net,
  rate
}`

Where task_earned is the dollar earned from tasks, goalused is the amount spent on goals, redemptions is number of money redemptions, avgTask is average earnings per task, avgGoal is average money spent per goal, net is total net loss/ gains in the given timeframe, and rate is the weekly earn rate.

##### /api/users/\<email\>
Methods: GET

Returns info on the user with email \<email\> including the following fields:

`{
  firstName,
  lastName,
  email,
  password,
  familyName,
  accountType,
  balance
}`


##### /api/addfriends
Methods: POST

Adds new friends for social/competitive element. Needs friend approval for each to see other's rankings. Send me a json with the following fields::

`{
  email,
  friend
}`

where email is the email of the user and friend is the inputted email of the friend to be invited. No checks on the friend email needs to be done on the front end.

##### /api/acceptfriends
Methods: POST

Once a user accepts a friend request notification, send me the following:

`{
  email,
  friend
}`

where email is the email of the user accepting the request and friend is the email of the friend that made the request.

##### /api/social/\<email\>
Methods: GET

Method to obtain social stats for all the friends of the user with email <email>. Returns a dictionary of dictionary, with the outer dictionary keyed on the email of a friend in the user's friend list and the inner dictionaries keyed on the following values:

`{
  tasksCompletedWeek,
  tasksCompletedWeek,
  goalsCompletedWeek,
  goalsCompletedMonth,
  taskCompletionRateWeek,
  taskCompletionRateMonth,
  firstName,
  lastName
}`

where the first four terms are the number of goals/tasks completed in their respective timeframes, the next two are completion percentages of tasks expressed as floats (ranging in value from 0.0 to 1.0) and firstName and lastName are strings of the first and last name of the friend, respectively.

##### /api/social/taskhistory/\<email\>
Methods: GET

Used for showing graph (number line) of task history for given user with email \<email\>. Returns a dictionary keyed on integers from 0 to 31, with values representing the number of tasks completed on that day. For example, a value of 5 and a key of 3 means that the user completed 5 tasks 3 days ago.

##### /api/\<email\>/credentials/\<password\>
Methods: POST

Asserts whether the <email> <password> combination is valid. Returns a json file with field:

`{
  Success
}`

where Success is True if combination is valid and False if combination is not. Status code is 201 if no email \<email\> is found, and 200 if \<email\> exists.

##### /api/goals/\<email\>
Methods: GET

GET: Returns list of goals assigned to child with email \<email\> in the format of a dictionary keyed on integers (0, 1, ...) to a dictionary with the following values (can be changed):

`{
    name,
    value,
    email,
    description,
    image,
    approved,
    redeemed
}`

where name is name of goal, value is cost of goal, email is email of child, image is a string address to the image, approved is 0 when it is pending parent approval, 1 when approved, and -1 when denied, and redeemed is a boolean.

##### /api/goals
Methods: POST

POST: Add new goal for user with email \<email\>, takes a json file with name payLoad and fields:

`{
    name,
    value,
    email,
    description,
    image,
}`

##### /api/goals/complete/<email>
Methods: GET

GET: Get a dictionary keyed on integers and with values corresponding to goals completed by the user in the identical format as the dictionary above.

##### /api/goals/incomplete/<email>
Methods: GET

GET: Get a dictionary keyed on integers and with values corresponding to goals that are still incomplete in the identical format as the dictionary above.

##### /api/goals/approve
Methods: POST

POST: Used so parents can approve the goals set by their kids. Send me a json file named payLoad with the following fields:

`{
    goalName,
    childEmail,
    approved,
    senderEmail
}`

where approved is an INTEGER that is 1 if approved and -1 if denied

##### /api/children/\<email\>
Methods: GET

Returns list of all children to the parent with email \<email\> in the format of a dictionary keyed on integers (0, 1, ...) and with each mapped to smaller dictionary with the following values (each representing a child):

`{
  firstName,
  lastName,
  email,
  password,
  familyName,
  accountType,
  balance
}`

##### /api/balance
Methods: POST

Updates balance of any user. Takes a json file named payLoad with following fields:

`{
  email,
  increment,
  senderEmail
}`

##### /api/tasks/completed
Methods: POST

Updates completion status of tasks. Send me a json file named payLoad with following fields:

`{
  email,
  taskName
}`

where email is the email of the child that completed the task, and taskName is name of the task.


##### /api/tasks/verified
Methods: POST

Updates verification status of tasks. Sends me a json file named payLoad with following fields:

`{
  email,
  taskName
}`

where email is the email of the child that completed the task, and taskName is name of the task.

##### /api/redeem
Methods: POST

Redeems a selected goal and updates balance accordingly. Post the following json named payLoad:

`{
  email,
  goalName
}`

where email is the email of the child that is redeeming the goal, and goalName is the name of the goal that is being redeemed.

##### /api/redeemmoney
Methods: POST
Redeems a selected goal and updates balance accordingly. Post the following json named payLoad:
`{ email,  $amount }`
where email is the email of the child that is redeeming the goal, and $amount is the float (no dollar sign) of amount redeemed


##### /api/notifications
Methods: POST

Alerts backend when a user reads/dismisses a notification, changing the read status from False to True. Post to me a json named payLoad with the following values:

`{
  email,
  priority
}`

where email is the email of the notified user (also in the notification dictionary structure) and priority is the priority field of the notification dictionary. Here it's as essentially an ID to help me identify which notification it is.

##### /api/delete
Methods: POST

Deletes single account; gives json file with following field:

`{
  email
}`

where email is the email of the account that wants to be deleted.

##### /api/deleteall
Methods: POST

Allows parents to delete all accounts including their children; gives json file with following field:

`{
  email
}`

where email is the email of their account; all children accounts associated with the family will be deleted.

##### /api/auth/forgotpassword
Methods: POST

Allows password change, also uses flask email which can be janky. Send me a post (with token) with following fields:

`{
  email
}`

##### /api/auth/changepassword
Methods: POST

Allows password change, also uses flask email which can be janky. Send me a post (with token) with following fields:

`{
  email
  password
  newPassword
}`

where password is the old password and newPassword is the password you want to change it to.

##### /api/color/\<email\>
Methods: POST, GET

Get returns the a dictionary with one key: color. Default is set to 0 and any legacy accounts will always have 0 as its color.

Post expects a dictionary named payLoad with one key: color. Value is any int you want the backend to store and return in subsequent GET calls.

##### /api/notifications/\<email\>
Methods: GET

Returns a dictionary keyed on integers (0, 1, ...) of notifications to be displayed for the user with email \<email\>. Importantly, this dictionary IS SORTED, with 0 being the most recent notification, 1 being the second most recent, and so forth. This get request is for both children and parents. Each key corresponds to a smaller dictionary with the following values:

`{
  email,
  accountType,
  notificationType,
  notificationName,
  description,
  senderName,
  senderEmail,
  priority,
  read,
  deadline,
  displayRed
}`
_*Both deadline and displayRed are only present for newTask notifications_

where email is the email of the recipient,

accountType is the accountType of the recipient, and

notificationType describes what type of notification it is. The following are the list of all possible notificationType: newTask (for children), newGoal (for parents), taskComplete (for parents), taskVerified (for children), taskUnverified (for children), balanceChange (for children), goalApproval (for both approved and denied goals), addRequest (for children, social), requestAccepted (for children, social) and goalComplete (for both adult and children).

notificationName is the name of the task for task-related notifications, name of the goal for goal-related notifications, and change in amount for balance-related notifications.

description is the description fields of the tasks/goals respectively. The only exception to this is for goalApproval events. In goalApproval notifications, description is "Goal Approved" when approved and "Goal Denied" when denied.

senderName and senderEmail are the name and email of the party that initiated the action (i.e. for a newTask notification, it would be the parent, for a goalComplete, it would be the child, etc.) - probably helpful for display on the front end, because you can go: "senderName has completed a task!"

priority, you don't have to worry about but it's just an int that I increment on the backend... the higher the int the more recent the notification. I also use this as its ID (since it is unique)

read is whether or not the user has already seen this notification. All notifications sent to you should have a read field of False

deadline is the string of the task's deadline

displayRed is a boolean that is true if the task is due in less than 24 hours
