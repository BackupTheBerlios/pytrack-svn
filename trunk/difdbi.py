""" This is the database interface.
"""
import sqlite
import types
from sqlite import *
from sqlite import DatabaseError

def DBOpen(dblogin):
    global _db
    if Database.db == None:
        try:
            Database.db = connect(dblogin)
        except DatabaseError, msg:
            print 'Could not open database: %s'%msg
        _db = None


def DBClose():
    if Database.db != None:
        Database.db.close()
        Database.db = None

def CachedDb():
    global _db
    if _db == None:
        _db = Database()
    return _db

class Database:
    db = None

    def __init__(self):
        pass

    def Sql(self, statement):
        try:
            self.cursor = self.db.cursor()
        except DatabaseError, msg:
            return "ERROR: Could not get cursor\nMessage: %s"%(statement, msg)
        try:
            self.cursor.execute(statement)
        except DatabaseError, msg:
            return "ERROR: Could not execute statement '%s'\nMessage: %s"%(statement, msg)
        return ""
    
    def Commit(self):
        try:
            self.db.commit()
        except DatabaseError, msg:
            return "ERROR: Could not commit the data.\nMessage: %s"%(statement, msg)
        return ""

    def _StripAttr(self, row):
        def _StripString(el):
            if type(el) == types.StringType:
                return el.strip()
            else:
                return el
        return tuple(map(_StripString,row))

    def _StripAttrAll(self, list):
        return map(self._StripAttr,list)

    def FetchAll(self):
        return self._StripAttrAll(self.cursor.fetchall())

    def FetchOne(self):
        return self.cursor.fetchone()

    def WriteTrack(self, track):
        """ Writes a garmin track into the database. """
        if len(track) > 0:
            trackhdr = track[0]
            #check if a track with this name already exists
            sqlError = self.Sql("SELECT * FROM tracks WHERE name='"+trackhdr.trk_ident+"'")
            if sqlError:
                print sqlError
            else:
                if len(self.FetchAll())>1:
                    #trackname exists already.
                    return -2
                else:
                    trackid = self.NextId("tracks")
                    sqlError = self.Sql("INSERT INTO tracks VALUES (%d, '%s', '', '')"%(trackid, trackhdr.trk_ident))
                    if sqlError:
                        print sqlError
                        return -1
                    else:
                        track = track[1:]
                        for trackpoint in track:
                            sqlError = self.Sql("INSERT INTO trackpoints VALUES (%d, %d, %f, %f, '%s', %f, %d)"%( self.NextId("trackpoints"), trackid, trackpoint.slat, trackpoint.slon, trackpoint.time, trackpoint.alt, trackpoint.new_trk))
                        self.Commit()
                        return 0
        else:
            return -1

    def ListTracks(self, labelId=-1):
        """ Returns a list with tracks and their id. """
        if labelId == -1:
            sqlError = self.Sql("SELECT id, name FROM tracks")
        else:
            sqlError = self.Sql("""
            SELECT t.id, t.name
            FROM tracks AS t, labels AS l, labeltrackrelation AS ltr
            WHERE t.id=ltr.trackid AND l.id=ltr.labelid AND l.id=%d
            """%(labelId,))
            
        if sqlError:
            print sqlError
            return []
        else:
            return self.FetchAll()
            
        
    def ListLabels(self):
        """ Returns a list with labels and their id. """
        sqlError = self.Sql("SELECT id, name FROM labels")
        if sqlError:
            print sqlError
            return []
        else:
            return self.FetchAll()
        
    def ListTrackPoints(self, trackId):
        """ Returns a list of trackpoints for the given list id. """
        sqlError = self.Sql("SELECT id, slon, slat, alt, time FROM trackpoints WHERE trackid=%d"%trackId)
        if sqlError:
            print sqlError
            return []
        else:
            return self.FetchAll()

    def DeleteTrackPoints(self, trackPointId):
        """ Deletes a track point from the list. """
        sqlError = self.Sql("DELETE FROM trackpoints WHERE id="+str(trackPointId))
        if sqlError:
            print sqlError
        
    def DeleteTrack(self, trackId):
        """ Deletes a track and his associated track points. """
        sqlError = self.Sql("DELETE FROM trackpoints WHERE trackid=%d"%(trackId,))
        if sqlError:
            print sqlError
        else:
            sqlError = self.Sql("DELETE FROM tracks WHERE id=%d"%(trackId,))
            if sqlError:
                print sqlError
            else:
                self.Commit()
                
    def RenameTrack(self, trackId, newName):
        """ Renames a track """
        sqlError = self.Sql("UPDATE tracks SET name='%s' WHERE id=%d"%(newName, trackId))
        if sqlError:
            print sqlError
        else:
            self.Commit()

    def NextId(self, table):
        """ Returns the next id of the given table. """
        self.Sql("SELECT max(id)+1 FROM %s"% table)
        id = self.FetchOne()[0]
        if not id:
            id=0
        return id


if __name__ == '__main__':
    DBOpen('test.dat')
    db = CachedDb()
    sqlError = db.Sql('''
    CREATE TABLE tracks (
      id INT PRIMARY KEY,
      name VARCHAR(100),
      description VARCHAR(255),
      date TIMESTAMP
    )
    ''')
    if sqlError:
        print sqlError

    sqlError = db.Sql('''
    CREATE TABLE trackpoints (
      id INT PRIMARY KEY,
      trackid INT REFERENCES tracks(id),
      slat DOUBLE,
      slon DOUBLE,
      time TIMESTAMP,
      alt DOUBLE,
      new_trk INT
    )
    ''')
    if sqlError:
        print sqlError

    sqlError = db.Sql('''
    CREATE TABLE labels (
      id INT PRIMARY KEY,
      name VARCHAR(100),
      description VARCHAR(255)
    )
    ''')
    if sqlError:
        print sqlError

    sqlError = db.Sql('''
    CREATE TABLE labeltrackrelation (
      labelid INT PRIMARY KEY REFERENCES labels(id),
      trackid INT REFERENCES tracks(id)
    )
    ''')
    if sqlError:
        print sqlError

    sqlError = db.Sql("INSERT INTO tracks VALUES (1, 'First Test', 'just a test', '12/8/04 12:00')")
    if sqlError:
        print sqlError
    sqlError = db.Sql("INSERT INTO trackpoints VALUES (1, 1, 46.53295, 6.56451, '2345', 300, 1)")
    if sqlError:
        print sqlError
    sqlError = db.Sql("INSERT INTO trackpoints VALUES (2, 1, 46.533456, 6.5345, '12345', 310, 0)")
    if sqlError:
        print sqlError
    sqlError = db.Sql("INSERT INTO labels VALUES (1, 'running training', '')")
    if sqlError:
        print sqlError
    sqlError = db.Sql("INSERT INTO labeltrackrelation VALUES (1, 2)")
    if sqlError:
        print sqlError
    db.Commit()
    DBClose()

    print "Done."
