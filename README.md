# SimpleICloud

SimpleiCloud is a lightweight iCloud client for Python, currently focused exclusively on managing contacts.

Unlike other libraries — such as the excellent [PyiCloud](https://github.com/picklepete/pyicloud) — SimpleiCloud aims to support a broader set of contact-related use cases, including creating, updating, and deleting contacts.

SimpleiCloud is powered by [requests](https://github.com/kennethreitz/requests) HTTP library.

This module is under active development, and we welcome contributions from the community.

## Examples
You must use an app-specific password for iCloud (generate it at <https://appleid.apple.com/> > Sign-In & Security > App-Specific Passwords)
### Package Installation
```python
pip install simple-icloud
```

### Class Instantiation
```python
from simple_icloud import SimpleICloudService

simpleicloudservice = SimpleICloudService(
    username="user@domain.com",
    password="secret_P422sword",
)
```
### Get a contact 
```python
contact = simpleicloudservice.get_contact("F4ZZZZ0-EZZ7-4ZZD-8ZZE-C4FZZZZZZACD")
```
### Get all contacts
```python
contacts_list = simpleicloudservice.get_all_contacts()
```
### Delete a contact
```python
contact = simpleicloudservice.delete_contact("F4ZZZZ0-EZZ7-4ZZD-8ZZE-C4FZZZZZZACD")
```
### Create a contact
#### create the vCard
```python
import uuid
import vobject
v = vobject.vCard()
v.add("fn").value = "Pippo DePippis"
# don't ask me why but iCloud need the following!
# credits to https://github.com/pimutils/vdirsyncer/issues/1145#issuecomment-2464999129
v.add("n").value = vobject.vcard.Name(family="DePippis", given="Pippo")
phone = v.add("tel")
phone.value = phone_
phone.type_param = "CELL"
email = v.add("email")
email.value = "pippo.depippis@xyz.abc"
email.type_param = ["INTERNET", "HOME", "pref"]
uuid_ = str(uuid.uuid4())
v.add("uid").value = uuid_
```
#### create the contact in iCloud
```python
simpleicloudservice.create_contact(vcard=v)
```
### Update a contact
#### edit the contact's feature
```python
email = v.add("email")
email.value = "blabla@aaa.com"
email.type_param = ["INTERNET", "HOME", "pref"]
```
#### update the contact in iCloud
```python
simpleicloudservice.update_contact(v)
```