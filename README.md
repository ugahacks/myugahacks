<p align="center">
  <img alt="UGAHacks 6" src="app/static/img/github-logo.png" width="80%"/>
</p>

## Features
- Account Sign-up and Login w/ Email Verification
- Social Authentication integration w/ Google, MLH, and GitHub
- Event registration form for hackers, mentors, volunteers
- Application review and status system for organizers
- QR code attendance system and scanner
- Statistics page for pre- and post-event data-crunching
- Blog w/ approval system
- Volunteer duty management system
- Meal and Workshop management systems
- Sponsor application view w/ export functionality
- Various user roles: organizer, sponsor, hacker, volunteer, director


## Setup

Needs: Python 3, virtualenv

- `git clone https://github.com/ugahacks/myugahacks && cd myugahacks`
- `python3 -m venv venv`
- `source ./venv/bin/activate`
- `pip install -r requirements.txt`
- (Important) If setting up on the productions server, set up the Postgres environment variables before the next steps
- `python manage.py migrate`
- `python manage.py createsuperuser` (creates an admin account which you use to access... the admin panel, duh)


## Running The App

### Local

- Set up (see above)
- `python manage.py runserver`
- Easy peasy, no more pesky docker

### Production

Setup based on this [tutorial](https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-18-04). Read it if you run into any problems.

- Set up (see above)
- Create server.sh from template: `cp server.sh.template server.sh`
- `chmod +x server.sh`
- Edit settings variables to match your environment
- Create restart.sh from template: `cp restart.sh.template restart.sh`
- `chmod +x restart.sh`
- Edit settings variables to match your environment
- Run `restart.sh`. This will update the database, dependecies and static files.
- Set up Systemd (read next section)

#### Setting Up Gunicorn
Needs: Systemd.

- Enter `sudo nano /etc/systemd/system/backend.service` (yes I use nano, fight me)
- Copy and paste the following:

```
[Unit]
Description=backend daemon
After=network.target

[Service]
User=user
Group=www-data
WorkingDirectory=/home/ugahacks/ugahacks5
ExecStart=/home/ugahacks/ugahacks5/server.sh >>/home/ugahacks/ugahacks5/out.log 2>>/home/ugahacks/ugahacks5/error.log

[Install]
WantedBy=multi-user.target
```

- Create and enable service: `sudo systemctl start backend && sudo systemctl enable backend`


#### Setting Up Postgres

Needs: PostgreSQL installed

- Enter PSQL console: `sudo -u postgres psql`
- Create database: `CREATE DATABASE backend;`
- Create user for database: `CREATE USER backenduser WITH PASSWORD 'password';` (make sure to include a strong password)
- Prepare a user for Django

```sql
ALTER ROLE backenduser SET client_encoding TO 'utf8';
ALTER ROLE backenduser SET default_transaction_isolation TO 'read committed';
ALTER ROLE backenduser SET timezone TO 'EST';
```

- Grant all priviledges to your user for the created database: `GRANT ALL PRIVILEGES ON DATABASE myproject TO myprojectuser;`
- Exit PSQL console: `\q`



#### Setting Up Nginx

Needs: Nginx

- `sudo nano /etc/nginx/sites-available/default`
- Add site:

```
server {
    listen 80;
    listen [::]:80;

    server_name my.ugahacks.com ugahacks.com;


    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        alias /home/ugahacks/ugahacks5/staticfiles/;
    }

    location /files/ {
        alias /home/ugahacks/ugahacks5/files/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/ugahacks/ugahacks5/backend.sock;
        client_max_body_size 5MB;
    }


}
```

#### Deploying New Versions

- `git pull`
- `./restart.sh`
- `sudo service backend restart`



## Management

### Automated Expiration

- Create management.sh from template: `cp management.sh.template management.sh`
- `chmod +x management.sh`
- Edit settings variables to match your environment
- Add to crontab: `crontab -e`
```
*/5 * * * * cd /home/ugahacks/ugahacks5/ && ./management.sh > /home/ugahacks/ugahacks5/management.log 2> /home/ugahacks/ugahacks5/management_err.log
```

### User Roles

- **is_volunteer**: Allows user to check-in hackers with QR and list view
- **is_organizer**: Allows user to vote on applications, scan hackers, create meals, and workshops.
- **is_director**: Allows user to send invites to hackers, and approve blog posts.
- **is_sponsor**: Allows user to view applications from hackers that came to the event ,and export resumes.
- **is_admin**: Allows user to enter Django Admin interface

### Important SQL Queries

Here are several queries that may be useful during the hackathon application process.

1. `source ./env/bin/activate`
2. `python manage.py dbshell`
3. Run SQL query
4. Extract results

#### Missing Applications Emails

Emails from users that have registered but have not completed the application.

```sql
SELECT u.email
FROM user_user u
WHERE NOT is_director AND NOT is_volunteer AND NOT is_organizer
AND u.id NOT IN
(SELECT a.user_id FROM applications_application a);
```


## Personalization

### Style

- Colors and presentation: [app/static/css/main.css](app/static/css/main.css).
- Navbar & content/disposition: [app/templates/base.html](app/templates/base.html)
- Email base template: [app/templates/base_email.html](app/templates/base_email.html)
- Update favicon [app/static/](app/static/)


### Content

#### Updating Email Templates:

You can update emails related to
- Applications (application invite, event ticket, last reminder, waitlist) at [applications/templates/mails/](applications/templates/mails/)
- Reimbursements (reimbursement email, reject receipt) at [reimbursement/templates/mails/](reimbursement/templates/mails/)
- User registration (email verification, password reset) at [user/templates/mails/](user/templates/mails/)

#### Updating Hackathon Variables
Check all available variables at [app/hackathon_variables.py.template](app/hackathon_variables.py.template).
You can set the ones that you prefer at [app/hackathon_variables.py](app/hackathon_variables.py)

#### Updating Registration Form
You can change the form, titles, texts in [applications/forms.py](applications/forms.py)

#### Updating Application Model
If you need to add extra labels, you can change the model and add additions fields.

   - Update model with specific fields: [applications/models.py](applications/models.py)
   - `python manage.py makemigrations`
   - `python manage.py migrate`


# License

MIT © UGAHacks
