# -------------------------------------------------------------------------------
# app.py
# Authors: Alan Ding    (Princeton '22, CS BSE)
#          Oleg Golev   (Princeton '22, CS BSE)
#          Gerald Huang (Princeton '22, EE BSE)
#
# Running module and the routing middle-tier.
# -------------------------------------------------------------------------------

from flask import *
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from CASClient import CASClient
from sys import argv, stderr
import os
import hashlib
import random
from base64 import b64encode
from datetime import datetime
import requests
import json

# -----------------------------------------------------------------------
#                          ENABLE / DISABLE CAS
# -----------------------------------------------------------------------

CAS = True

# -----------------------------------------------------------------------
#                         APP AND DATABASE SETUP
# -----------------------------------------------------------------------

appl = Flask(__name__, template_folder="templates", static_folder="static")
appl.secret_key = os.environ.get('SECRET_KEY')

mail_settings = {
    "MAIL_SERVER": os.environ.get('MAIL_SERVER'),
    "MAIL_PORT": os.environ.get('MAIL_PORT'),
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": os.environ.get('MAIL_USERNAME'),
    "MAIL_PASSWORD": os.environ.get('MAIL_PASSWORD'),
    "MAIL_DEFAULT_SENDER": os.environ.get('MAIL_DEFAULT_SENDER')
}

appl.config.update(mail_settings)
mail = Mail(appl)

# -------------- !!! COMMENT OUT IF RUNNING ON HEROKU !!! -------------- #
# from private import USER, PW, HOST, DB_NAME
# DB_URL = "postgresql+psycopg2://{0}:{1}@{2}/{3}".format(USER, PW, HOST, DB_NAME)
# appl.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
# ---------------------------------------------------------------------- #

# --------------- !!! COMMENT OUT IF RUNNING LOCALLY !!! --------------- #
appl.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
# ---------------------------------------------------------------------- #

appl.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(appl, engine_options={'pool_pre_ping': True, 'pool_size': 20, 'max_overflow': 0})

from db_functions import addUser, addCrush, getRemCrushes, getSecretAdmirers, \
    getFormattedStudentInfoList, getCrushes, getMatches, getName, isUser, \
    isFirstTime, removeFirstTime

from send_emails import send_match_email, send_welcome_email
from get_local_students import getLocalStudents

# -----------------------------------------------------------------------
#                           AUTHENTICATION
#                 !!! COMMENT OUT IF RUNNING LOCALLY !!!
# -----------------------------------------------------------------------


# returns the username and True or an error message and False
def check_user(session):
    if CAS:
        username, err = CASClient().authenticate('netid')
        return username, err
    else:
        if 'netid' in session:
            return session['netid'], False
        else:
            err = "Please log in before using this application."
            return err, True

# -----------------------------------------------------------------------


@appl.route('/login_user', methods=['GET'])
def login_user():

    invalid_user_err = "Unfortunately, your netid cannot be found in the " + \
                       "Tigerbook database. TigerCrush currently supports " + \
                       "only listed undergraduates. We will work to " + \
                       "accommodate more people in the future. Sorry for " + \
                       "the inconvenience."

    if CAS:
        username, err = CASClient().authenticate('netid')
        if err:
            return redirect(url_for('login', err=username))
        return redirect(url_for('index'))

    else:
        netid = request.args.get('netid')
        if netid == None or netid.strip() == '':
            err = "Please enter your netid to use this application."
            return redirect(url_for('login', err=err))
        if not isUser(netid):
            return redirect(url_for('login', err=invalid_user_err))

        session['netid'] = netid
        return redirect(url_for('index'))

# -----------------------------------------------------------------------
#                           PER-REQUEST SETUP
#                 !!! COMMENT OUT IF RUNNING LOCALLY !!!
# -----------------------------------------------------------------------


@appl.before_request
def redirectHTTP():
    # redirect http to https
    if request.url[0:5] != 'https':
        return redirect(request.url.replace('http', 'https', 1))

# -----------------------------------------------------------------------
#                         PAGE ROUTING SECTION
# -----------------------------------------------------------------------


@appl.route('/')
@appl.route('/login')
def login():

    err = request.args.get('err')
    if err is not None:
        html = render_template("login.html", err=err)
    else:
        html = render_template("login.html", CAS=CAS)
    return make_response(html)

# -----------------------------------------------------------------------


@appl.route('/register', methods=['GET'])
def register():

    netid, err = check_user(session)
    if err:
        return redirect(url_for('login', err='CAS authentication failed.'))

    if isUser(netid):
        return redirect(url_for('index', err="Already registered."))

    html = render_template("register.html")
    return make_response(html)

# -----------------------------------------------------------------------


@appl.route('/register_user', methods=['POST'])
def register_user():

    netid, err = check_user(session)
    if err:
        return redirect(url_for('login', err='CAS authentication failed.'))

    if isUser(netid):
        return redirect(url_for('index', err="Already registered."))

    first_name = request.form['first-name']
    last_name = request.form['last-name']
    class_year = request.form['class-year']

    addUser(netid, " ".join(first_name, last_name), class_year)

    return redirect(url_for('index', err='Congratulations! You can now use TigerCrush!'))

# -----------------------------------------------------------------------


@appl.route('/index')
def index():

    # validate the current user session
    netid, err = check_user(session)
    if err:
        return redirect(url_for('login', err='CAS authentication failed.'))

    if not isUser(netid):
        # redirect them to a different form page to enter information about themselves
        return redirect(url_for('register'))

    err = request.args.get('err')
    if err is None:
        err = ""

    firstTime = isFirstTime(netid)
    remCrushes = getRemCrushes(netid)
    numSecretAdmirers = getSecretAdmirers(netid)
    matched = len(getMatches(netid)) > 0
    name = getName(netid).split()
    if name == '(unregistered user)':
        name = netid
    else:
        name = name[0]

    if firstTime:
        # we display a banner about ProofPoint blocking our emails and 
        # send a welcome email accordingly
        removeFirstTime(netid)
        send_welcome_email(netid)

    html = render_template("index.html",
                           netid=netid,
                           name=name,
                           remCrushes=remCrushes,
                           firstTime=firstTime,
                           numSecretAdmirers=numSecretAdmirers,
                           matched=matched,
                           err=err)

    return make_response(html)

# -----------------------------------------------------------------------


@appl.route('/faq')
def faq():
    html = render_template("faq.html")
    return make_response(html)

# -----------------------------------------------------------------------


@appl.route('/about')
def about():
    html = render_template("about.html")
    return make_response(html)

# -----------------------------------------------------------------------


@appl.route('/whitelist')
def whitelist():
    html = render_template("whitelist.html")
    return make_response(html)

# -----------------------------------------------------------------------
#                        ENDPOINTS FOR REQUESTS
# -----------------------------------------------------------------------


# helper endpoint that returns formatted Tigerbook data
@appl.route('/studentInfo')
def studentInfo():

    # validate the current user session
    netid, err = check_user(session)
    if err:
        return redirect(url_for('login', err=netid))

    return {'data': getFormattedStudentInfoList()}

# -----------------------------------------------------------------------


# gets and formats (into a list of strings to be displayed) the crushes
# for the user with the specified netid
@appl.route('/getCrushes')
def crushes():
    # validate the current user session
    netid, err = check_user(session)
    if err:
        return redirect(url_for('login', err=netid))

    url_netid = request.args.get('netid')
    if netid != url_netid:
        return {'data': []}

    crushList = getCrushes(netid)
    return {'data': [getName(crush.crushed_on) for crush in crushList]}

# -----------------------------------------------------------------------


# gets and formats (into a list of strings to be displayed) the matches
# for the user with the specified netid
@appl.route('/getMatches')
def matches():
    # validate the current user session
    netid, err = check_user(session)
    if err:
        return redirect(url_for('login', err=netid))

    url_netid = request.args.get('netid')
    if netid != url_netid:
        return {'data': []}

    matchList = getMatches(netid)
    return {'data': ['%s (%s@princeton.edu)' % (getName(match), match)
                     for match in matchList]}

# -----------------------------------------------------------------------


# adds a crush (crushNetid arg) for a given user (netid)
@appl.route('/addCrush', methods=['GET', 'POST'])
def addCrushEndpoint():
    # validate the current user session
    netid, err = check_user(session)
    if err:
        return redirect(url_for('login', err=netid))

    if request.method == 'POST':
        crushNetid = request.form.get('crushNetid')
        crushNetid = crushNetid.split(' ', 1)[0]

        print('addCrush netid argument value: ' + netid)
        print('addCrush crushNetid argument value: ' + crushNetid)

        matched, err = addCrush(netid, crushNetid)
        if matched:
            send_match_email(netid, crushNetid)

    if err is not None:
        err = ""
    return redirect(url_for('index', netid=netid, err=err))

# -----------------------------------------------------------------------
#                   DATABASE INITIALIZATION COMMANDS
# -----------------------------------------------------------------------


# resets the database such that it consists of just a list of students and no
# crushes between any two students
from db_models import Crush, User
from sqlalchemy import or_


@appl.cli.command(name='createDB')
def createDB():

    User.__table__.create(db.engine, checkfirst=True)
    Crush.__table__.create(db.engine, checkfirst=True)
    db.session.commit()

    print('Done!\n')

    print('Trying to fetch students from TigerBook...', flush=True)
    # print('Trying to fetch students locally...', flush=True)

    # grab data
    students = getStudents()

    print('Deleting existing student data... ', end='', flush=True)

    db.drop_all()
    db.create_all()
    db.session.commit()

    print('Done!')

    print('Populating database with student data... ', end='', flush=True)

    # create rows in the db for each student
    for student in students:
        netid = student['net_id']
        name = student['full_name']
        year = student['class_year']
        addUser(netid, name, year)

    print('Done!')


@appl.cli.command(name='resetDB')
def resetDB():
    if input("Do you wish to DELETE the DEVELOPERS' CRUSH DATA? Enter y or n: ") != 'y':
        return

    devs = ['ajding', 'gh14', 'ogolev']
    dev_crushes = Crush.query.filter(or_(Crush.crushing == x for x in devs))
    print(dev_crushes.all())
    dev_crushes.delete()
    db.session.commit()

    print('Done! Updated dev crush query returned: ')
    dev_crushes = Crush.query.filter(or_(Crush.crushing == x for x in devs))
    print(dev_crushes.all())
    print()

    if input('Do you wish to DELETE ALL existing CRUSH DATA? Enter y or n: ') != 'y':
        return

    print('Deleting all existing crush data... ', end='', flush=True)

    # drop all previous crush data
    Crush.__table__.drop(db.engine, checkfirst=True)
    Crush.__table__.create(db.engine, checkfirst=True)
    db.session.commit()

    print('Done!\n')

    print('Trying to fetch students from TigerBook...', flush=True)
    # print('Trying to fetch students locally...', flush=True)

    # grab data
    students = getStudents()
    # students = getLocalStudents()

    print('Here is a snapshot of what was returned:')
    print(students[0:5])
    print()

    if input('Would you like to proceed with DELETING existing STUDENT DATA ' +
             'and REPOPULATING the database with what TigerBook returned? ' +
             'Enter y or n: ') != "y":
        print('resetDB exited: crush data cleared, student data untouched')
        return

    print('Deleting existing student data... ', end='', flush=True)

    db.drop_all()
    db.create_all()
    db.session.commit()

    print('Done!')

    print('Populating database with student data... ', end='', flush=True)

    # create rows in the db for each student
    for student in students:
        netid = student['net_id']
        name = student['full_name']
        year = student['class_year']
        addUser(netid, name, year)

    print('Done!')

# -------------------------------------------------------------------------------


# ONLY USE ON OTHER USERS WITH THEIR PERMISSION AND FOR TESTING PURPOSES
@appl.cli.command(name='userStats')
def userStats():
    netid = input('netid of user to be checked: ')
    user = User.query.filter_by(netid=netid).one()

    print()
    print('First time? ' + str(user.firstTime))
    print('Max number of secret admirers: ' + str(user.secretAdmirers))

    print()
    curr_secret_admirers = getSecretAdmirers(netid)
    print(curr_secret_admirers)

# -------------------------------------------------------------------------------


# dummy inefficient lol
@appl.cli.command(name='usageStats')
def usageStats():
    users = db.session.query(User)
    num_users = users.count()
    num_crushes = db.session.query(Crush).count()
    num_loggedin_users = db.session.query(User).filter_by(firstTime=False).count()
    num_matches = sum(len(getMatches(user.netid)) for user in users) // 2

    print('User table size: ' + str(num_users))
    print('Crush table size: ' + str(num_crushes))
    print('Number of users who have logged in at least once: ' + str(num_loggedin_users))
    print('Number of matched edges: ' + str(num_matches))
    print('Remaining capacity: ' + str(10000 - num_users - num_crushes))

# -------------------------------------------------------------------------------


@appl.cli.command(name='addUser')
def add_user():
    netid = input("netid: ")
    name = input("name: ")
    year = input("class year: ")

    if input("confirm (y/n): ") != 'y':
        return

    addUser(netid, name, year)
    print("New user successfully added!")

# -------------------------------------------------------------------------------


# helper function that returns a Python dict of data grabbed from TigerBook
def getStudents():
    url = 'https://tigerbook.herokuapp.com/api/v1/undergraduates'
    created = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    nonce = ''.join([random.choice(
        '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+/') for
        i in range(32)])
    username = 'ajding'
    password = os.environ.get('TIGERBOOK_KEY')
    generated_digest = b64encode(hashlib.sha256(
        nonce.encode('utf-8') + created.encode('utf-8') + password.encode(
            'utf-8')).digest()).decode()
    headers = {
        'Authorization': 'WSSE profile="UsernameToken"',
        'X-WSSE': 'UsernameToken Username="%s", PasswordDigest="%s", Nonce="%s", Created="%s"' % (
            username, generated_digest, b64encode(nonce.encode()).decode(),
            created)
    }

    r = requests.get(url, headers=headers)
    return json.loads(r.text)

# -----------------------------------------------------------------------
#                            MAIN METHOD
# -----------------------------------------------------------------------
# Requires a port number as a command-line argument. Starts the app.
# -----------------------------------------------------------------------


if __name__ == '__main__':

    if len(argv) != 2:
        print("Usage: " + argv[0] + " [port]", file=stderr)
        exit(1)

    try:
        ret = int(argv[1])
    except:
        print("Port must be an integer", file=stderr)
        exit(1)

    appl.run(host="0.0.0.0", port=int(argv[1]))

# -----------------------------------------------------------------------
