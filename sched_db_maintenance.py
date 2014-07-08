#!/usr/bin/env python2

import threading
import MySQLdb
import sched_config as conf


#Globals
lock = threading.Lock()

class Util:
   """ Utility functions for the Scheduler """
   def __init__(self):
      db = MySQLdb.connect(host=conf.dbconfig['dbhost'],
                     user=conf.dbconfig['dbuser'],
                     passwd=conf.dbconfig['dbpass'],
                     db=conf.dbconfig['dbname'])
      self.curs = db.cursor()

   def runQuery(self, query):
      lock.acquire()
      try:
         self.curs.execute(query)
      except MySQLdb.IntegrityError:
         return None
      finally:
         lock.release()
      result = self.curs.fetchall()
      return result

def DB_Cleanup():
   util = Util()

   jobs = util.runQuery("SELECT id, log_retention from jobs")
   for job in jobs:
      util.runQuery("DELETE from results where end_date < DATE_SUB(now(), INTERVAL %s DAY) and id=%s" % (job[1], job[0]))
      #print "DELETE from results where end_date < DATE_SUB(now(), INTERVAL %s DAY) and id=%s" % (job[1], job[0])


if __name__ == "__main__":
   DB_Cleanup()

