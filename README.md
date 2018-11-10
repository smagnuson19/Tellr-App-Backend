# Teller Backend

### Most of functionality doccumentation on [Frontend](https://github.com/dartmouth-cs98/18f-tellr-frontend) readme like specified in scaffolding assignment

# Tellr

Organize and streamline task assignment and chores in your household while teaching your kids the value of money! (testing branches and merging)

![alt text](https://github.com/dartmouth-cs98/18f-tellr-frontend/blob/master/Data%20Model%20and%20Sketches/profile.png)

## Architecture

MongoDB, Pymongo, Flask, RestAPI

#### Tech Stack
We are using React Native for our frontend and mobile app and flask for our backend

#### Data Objects and Methods

Our two primary data objects are the parentUser and the childUser. We currently believe we will be using three more secondary data objects to track transactions between the parentUsers and childUsers.

##### /api/childtasks/<email>
Methods: GET

Returns list of tasks assigned to child with email <email> in the format of a dictionary keyed on integers (0, 1, ...) to a dictionary with the following values:

`{
  taskName,
  reward,
  taskDeadline,
  taskDescription,
  childEmail,
  complete,
  verified,
  dateCompleted,
  familyName
}`

##### /api/parenttasks/<familyName>
Methods: GET

Returns list of tasks assigned to all children in given familyName <familyName> in the format of a dictionary keyed on integers (0, 1, ...) to a dictionary with the following values:

`{
  taskName,
  reward,
  taskDeadline,
  taskDescription,
  childEmail,
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
  complete,
  verified,
  dateCompleted,
  familyName
}`

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

##### /api/users/<email>
Methods: GET

Returns info on the user with email <email> including the following fields:

`{
  firstName,
  lastName,
  email,
  password,
  familyName,
  accountType,
  balance
}`

##### /api/<email>/credentials/<password>
Methods: POST

Asserts whether the <email> <password> combination is valid. Returns a json file with field:

`{
  Success
}`

where Success is True if combination is valid and False if combination is not. Status code is 201 if no email <email> is found, and 200 if <email> exists.

##### /api/goals/<email>
Methods: POST, GET

GET: Returns list of goals assigned to child with email <email> in the format of a dictionary keyed on integers (0, 1, ...) to a dictionary with the following values (can be changed):

`{
    Name,
    Prize,
    email,
    Description
}`

POST: Add new goal for user with email <email>, takes a json file with name payLoad and fields:

`{
    Name,
    Prize,
    email,
    Description
}`

##### /api/children/<email>
Methods: GET

Returns list of all children to the parent with email <email> in the format of a dictionary keyed on integers (0, 1, ...) and with each mapped to smaller dictionary with the following values (each representing a child):

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
  increment
}`
