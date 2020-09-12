# -------------------------------------------------------------------------------
# db_functions.py
# Authors: Alan Ding   (Princeton '22, CS BSE)
#          Oleg Golev  (Princeton '22, CS BSE)
#          Gerald Huang (Princeton '22, ELE BSE)
#
# Defines back-end API for enabling dynamic manipulation of the website front end.
# -------------------------------------------------------------------------------

from app import db
from db_models import User, Crush

# -------------------------------------------------------------------------------
#                                 addUser()
# -------------------------------------------------------------------------------
# Add a user to the database. There are two uses.
# (1) Helper function for initializing the database
# (2) If the user is not an undergraduate or is not on TigerBook, let the user
#     add themselves to the system manually. year field will be "GRAD" if it is
#     a graduate student, "STAFF" if it is a professor or a post-doc researcher.
#
# Upon success, return 0. Upon failure, print a descriptive error and return a
# user-readable error to display on the web page.
# -------------------------------------------------------------------------------

def addUser(netid, name, year):
    # below is my shitty code for the secret admirers issue
    # your code's not shitty homie ily <3
    user = User(netid=netid, name=name, year=year, visible=True, secretAdmirers=0)
    # user = User(netid=netid, name=name, year=year, visible=True)
    db.session.add(user)
    db.session.commit()

# -------------------------------------------------------------------------------
#                                 addCrush()
# -------------------------------------------------------------------------------
# Take two netid's represented as strings to add a new entry to the crush table.
# Call attemptMatch() executing in a new thread before returning.
#
# Returns whether the added crush resulted in a match.
# -------------------------------------------------------------------------------

def addCrush(crushing, crushed_on):
    # do nothing if user attempts to crush on themselves
    if crushing == crushed_on:
        return False, "We love to see self love, but you're probably " + \
                      "using TigerCrush to get matched to someone else. " + \
                      "For this reason, we don't allow you to add yourself " + \
                      "as your own crush. Sorry!"

    # send user error if crush already exists
    existing = db.session.query(Crush) \
        .filter_by(crushing=crushing, crushed_on=crushed_on) \
        .all()

    if len(existing) > 0:
        return False, "Looks like you're already crushing on the person " + \
                      "you just tried to add."

    # send user error if user is already at the crush limit
    if getRemCrushes(crushing) <= 0:
        return False, "You've reached the limit for the number of crushes you can add."

    crush = Crush(crushing=crushing, crushed_on=crushed_on)
    db.session.add(crush)
    db.session.commit()
    # return isMatch(crushing, crushed_on), None

    # below is my shitty code to try to fix the secret admirers issue
    user = db.session.query(User).filter_by(netid=crushed_on).first()
    if user is not None and not isMatch(crushing, crushed_on):
        user.secretAdmirers = max(user.secretAdmirers, getSecretAdmirers(user.netid))
        db.session.commit()

    return isMatch(crushing, crushed_on), None


# -------------------------------------------------------------------------------
#                                   isMatch()
# -------------------------------------------------------------------------------
# Checks whether there are two inverse entries in the crush table. If so, a match
# has been found. Send a one-time email with contact information to the two users.
#
# Returns whether netid1 and netid2 mutually crush on each other.
# -------------------------------------------------------------------------------

def isMatch(netid1, netid2):
    return netid2 in getCrushNames(netid1) and netid1 in getCrushNames(netid2)

# -------------------------------------------------------------------------------
#                                  getCrushes()
# -------------------------------------------------------------------------------
# Retrieve (by netid) a user's crushes as a list of dictionaries with fields:
#   netid: ""
#   name: ""
#   year: (int)
#
# Upon failure, print a descriptive error and return a ser-readable error to
# display on the web page.
# -------------------------------------------------------------------------------

def getCrushes(netid):
    crushes = Crush.query.filter_by(crushing=netid).all()
    # print('crushes:')
    # print(crushes)
    return crushes

# -------------------------------------------------------------------------------
#                                  getCrushNames()
# -------------------------------------------------------------------------------
# Retrieve (by netid) a user's crushes as a list of netids (strings)
#
# Upon failure, print a descriptive error and return a ser-readable error to
# display on the web page.
# -------------------------------------------------------------------------------

def getCrushNames(netid):
    crushes = getCrushes(netid)
    return [crush.crushed_on for crush in crushes]

# -------------------------------------------------------------------------------
#                                  getName()
# -------------------------------------------------------------------------------
# Returns the name of the student with the given netid
#
# Upon failure, print a descriptive error and return a ser-readable error to
# display on the web page.
# -------------------------------------------------------------------------------

def getName(netid):
    user = db.session.query(User).filter_by(netid=netid).first()
    if user is not None:
        return "%s, %s" % (user.name, user.year)
    else:
        return "(unregistered user)"

# -------------------------------------------------------------------------------
#                                  getMatches()
# -------------------------------------------------------------------------------
# Retrieve (by netid) a user's matches as a list of netids
#
# Upon failure, print a descriptive error and return a ser-readable error to
# display on the web page.
# -------------------------------------------------------------------------------

def getMatches(netid):
    myCrushes = getCrushNames(netid)

    crushingOnMeRows = db.session.query(Crush) \
        .filter_by(crushed_on=netid) \
        .all()

    crushingOnMe = [crush.crushing for crush in crushingOnMeRows]
    matches = list(set(myCrushes) & set(crushingOnMe))

    # for debugging purposes only! delete later
    # print('matches:')
    # print(matches)
    return matches

# -------------------------------------------------------------------------------
#                              getRemCrushes()
# -------------------------------------------------------------------------------
# Retrieve the remaining number of crushes that a given person may have. For
# this application, this is 5 + 1 more for each secret admirer minus the number
# of crushes that the given person already has.
#
# Upon success, return the maximum number of crushes. Upon failure, print a
# descriptive error and return a ser-readable error to display on the web page.
# -------------------------------------------------------------------------------

def getRemCrushes(netid):
    # return max(5 + getSecretAdmirers(netid) - len(getCrushes(netid)), 0)

    # here's my shitty code again 
    user = db.session.query(User).filter_by(netid=netid).first()

    if user is not None:
        return max(5 + user.secretAdmirers - len(getCrushes(netid)), 0)
    return 0

# -------------------------------------------------------------------------------
#                              getSecretAdmirers()
# -------------------------------------------------------------------------------
# Retrieve the secret admirers that a given person has.
#
# Upon success, return a list of admirers. Upon failure, print a descriptive
# error and return a user-readable error to display on the web page.
# -------------------------------------------------------------------------------

def getSecretAdmirers(netid):
    myCrushes = getCrushNames(netid)
    print('my crushes:')
    print(myCrushes)

    crushingOnMeRows = db.session.query(Crush) \
        .filter_by(crushed_on=netid) \
        .all()

    crushingOnMe = [crush.crushing for crush in crushingOnMeRows]
    print('crushing on me:')
    print(crushingOnMe)

    secretAdmirers = list(set(crushingOnMe) - set(myCrushes))

    # all prints for debugging purposes only! delete later
    print('secret admirers:')
    print(secretAdmirers)
    return len(secretAdmirers)

# -------------------------------------------------------------------------------
#                         getFormattedStudentInfoList()
# -------------------------------------------------------------------------------
# Returns a dictionary of all students' netids, names, and class years to be
# used by the front-end's autocompletion interface
# -------------------------------------------------------------------------------

def getFormattedStudentInfoList():
    users = User.query.all()
    r = ['%s - %s, %s' % (user.netid, user.name, user.year) for user in users]
    return r

# -------------------------------------------------------------------------------

def isUser(netid):
    user = db.session.query(User).filter_by(netid=netid).first()
    if user is None:
        return False
    return True

# -------------------------------------------------------------------------------

def isFirstTime(netid):
    user = db.session.query(User).filter_by(netid=netid).first()
    if user is not None:
        return user.firstTime

    return False

# -------------------------------------------------------------------------------

def removeFirstTime(netid):
    user = db.session.query(User).filter_by(netid=netid).first()
    if user is not None:
        user.firstTime = False
        db.session.commit()

# -------------------------------------------------------------------------------
