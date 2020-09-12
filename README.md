# TigerCrush

The one and only Tinder-defying application specifically for Princeton students. Add your crushes and see if they crush on you back. Revive your hopes and live your dreams with the love of your life through TigerCrush!

This app is a revival of the old GoodCrush platform, the brainchild of Josh Weinstein '09. It retains very similar functionality, allowing students to indicate as many crushes as they wish, and contacting two matched students if and only if the first student put down the second as a crush and vice versa. Users will also be able to see the number of students crushing on them whom they did not indicate to be a crush of their own. No "missed connection" feature is planned, since we believe Tiger Confessions++ serves that purpose already. Princeton students must log on with Princeton's CAS (Central Authentication Service), so the platform is closed to Princeton students only.

Features to be implemented in the next release:
- Add a random delay before sending an email/displaying a match so that users can't tell who was the one to "choose first"
- Add functionality for secret admirer messages: when you add a crush, you can also send a short message along to the person you're crushing on and the message will appear in the crushed on user's secret admirer message logs
- Display total number of crushes reported
- Auto-redirect to index if already logged in
- Manually add name/year if not in the database
- Add number of matches in usageStats script

## Local PostgreSQL Setup:
In order to properly use a PostgreSQL database and therefore the application on your machine, you must have a local PostgreSQL server and a GUI of your choice for editing and accessing your databases interactively.

### PostgreSQL Server
***
```Postgres.app``` is the preferred piece of software whose sole purpose is to initialize and run a PostgreSQL server. Please navigate to [this website](https://postgresapp.com/) and follow instructions for installing and setting up the application.

### PostgreSQL GUI
***
While ```Postgres.app``` includes a command-line interface, it is not as visually pleasing as a full-feature GUI. We will use ```pgAdmin 4``` to accomplish that goal. Please download the latest version of the application [here](https://www.pgadmin.org/).

After installation, open the application. You will be prompted to set a password when using PostgreSQL. Please set a password you can remember and select **Remember Password**. This way you will not have to re-enter the password every time you want to connect to a local database.

Make sure there is a server displayed on the left panel that is running on ```localhost```. If not, right-click ```Servers```, then select ```Create -> Server...```. Under ```General```, set the ```Name``` to be ```local```. Under ```Connection```, type ```localhost``` as the ```Host name/address```. Finally, press ```Save```.

(Optional) Remove all servers but one that you will be using by right-clicking each server under ```Servers(-)``` in the top-left corner of the page and the selecting ```Remove Server```. 

On the left panel, you will be able to see your server and all contained database. Right-click ```Databases(-)``` and select ```Create -> Database...```. Under ```General```, set the ```Database``` field to ```TigerCrush```. Press ```Save```.

Now you are all set up with the GUI!

### Python
***
Please install a psycopg2 package which acts as a PosgreSQL connection port. On a MacOS system, you can do this using pip:
```
pip install psycopg2-binary
```
As the last step, navigate to your TigerCrush working directory. First, edit ```private.py``` according to the instructions in the file and run the ```db_create.py``` using the following:
```
python3 db_create.py
```
This will create the schema under your TigerCrush PostgreSQL database we made earlier.

Now you are all set to enjoy the power of PostgreSQL locally. Enjoy!
