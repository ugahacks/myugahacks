UGAHacks5
-------------------------------------------------
* Ensure you have Python3 installed on your machine *


LOCAL SETUP INSTRUCTIONS
-------------------------------------------------

1. Clone this repo by entering "git clone https://github.com/ugahacks/ugahacks5" into bash.
2. Once inside the ugahacks5 directory, setup the virtual environment by entering "python3 -m venv venv". (This assumes you have "virtualenv" installed. If this command fails then install it with "python3 -m pip install --user virtualenv" on Mac/Linux or "py -m pip install --user virtualenv" for Windows peasants.
3. Once the virtualenv has been created, activate it by typing ". venv/bin/activate". You can tell if the venv is active by checking if "(venv)" shows up in front of your machine name in bash.
4. Install the required packages by entering "pip install -r requirements.txt".
5. Create & migrate the server by typing "python manage.py migrate".
6. Finally to run the app enter "python manage.py runserver --settings=ugahacks5.settings.local".
