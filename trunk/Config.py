import sys, os
import difdbi

#this list specifies how to log into the database
VERSION = "0.1"

serialDevice = "/dev/tty.usbserial0"

if sys.platform == "posix" or sys.platform == "darwin":
    dbfile = os.environ["HOME"]+"/.pytrack/db.dat"

elif sys.platform == "win32":
    dbfile = "db.dat"

try:
    exists = os.stat(dbfile)
except OSError:
    #file does not exist yet. Create it
    if sys.platform == "posix" or sys.platform == "darwin":
        try:
            os.mkdir(os.environ["HOME"]+"/.pytrack")
        except OSError:
            #do nothing if the path already exists
            pass
    difdbi.createDb(dbfile)

