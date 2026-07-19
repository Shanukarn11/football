# How to setup IKF Repo

- Install Python 10.1.0
- Install MySQL Community Server and setup

## Database Setup

Open terminal and run the below command to run the MySQL as root user
```
mysql -u root -p
```

Run command:
```
CREATE DATABASE indiakhelofootball CHARACTER SET utf8 COLLATE utf8_general_ci;
CREATE USER 'indiakhelofootball'@'localhost' IDENTIFIED BY 'indiakhelofootball';
GRANT ALL PRIVILEGES ON indiakhelofootball .* TO 'indiakhelofootball'@'localhost' WITH GRANT OPTION;
CREATE USER 'indiakhelofootball'@'%' IDENTIFIED BY 'indiakhelofootball';
GRANT ALL PRIVILEGES ON indiakhelofootball.* TO 'indiakhelofootball'@'%' WITH GRANT OPTION;
flush privileges;
```

Now Run the Migrations and Migrate

```
python manage.py makemigrations
python manage.py migrate
```

Now you can run the server or can import the database

## Import Database
Copy the backup DB file to location /usr/local/bin/mysql, you can find the location of MySQL by running the below command 
```
which mysql
```

Open the Terminal and change the location to sql and backup.sql and run the following command to import:
```
mysql -u root -p indiakhelofootball < backupDBName.sql
```
##import csv

## Project Setup

Create a virtual venv with version 3.10

 ```bash
 python3.10 -m venv venv
 ```
Activate the Virtual venv

```bash
source venv/bin/activate   # macOS/Linux
venv/Scripts/activate      # Windows
```

Install the dependencies from requirement.txt file.
```bash
pip install -r requirement.txt
```

Make sure pip & setuptools are uptodate.
```bash
pip install --upgrade pip
pip install -r setuptools
```

Change Directory to IKF:
```bash
python manage.py runserver
```

To create the migrations create a folder with name "migrations" in the main folder and __init__.py file within the Folder and run the following commands :

```
python manage.py makemigrations
python manage.py migrate
```

if face any mySQL version problem add the following code under the DB of settings.py
```
'OPTIONS': {
            'charset': 'utf8mb4',  # Use utf8mb4 for full Unicode support, including emojis
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
```

Run the server:
```
python manage.py runserver
```

To update the requirements.txt file in your Django project
```
pip freeze > requirements.txt
```
test
CSV file import

```
python manage.py shell

import csv
import os
from ikf.models import Scout

file_path = os.path.join('ikf', 'csv', 'scoutdata.csv')

with open(file_path, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        Scout.objects.create(
            full_name=row['Full Name'],
            location=row['Location'],
            preferred_cities=row['Preferred Cities where you can Scout'],
            mobile_number=row['Mobile Number'],
            gmail_id=row['Gmail ID'],
            linkedin=row['Linkedin Handle (Enter Link)'],
            instagram=row['Instagram Handle (Enter Link)'],
            facebook=row['Facebook Handle (Enter Link)'],
            ikf_tshirt=row['Do you have IKF T-Shirt ?'].strip().lower() in ['yes', 'true', '1'],
            pan_number=row['PAN Number'],
            bank_details=row['Bank Account Details'],
            profile_photo=row['Upload Your Profile Photo in PNG Format'] or ''
        )




```
