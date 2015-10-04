#!/usr/bin/env python2

import sys, os
import socket, ssl, threading, time
import SocketServer
import string
import random
import cPickle
import logging
import  datetime as dt
from datetime import datetime, timedelta
from apscheduler.scheduler import Scheduler
from email.mime.text import MIMEText
import MySQLdb
import sched_config as conf
from pprint import pprint
from OpenSSL import crypto, SSL

#Global defs
logging.basicConfig()
myself = socket.gethostbyname(socket.gethostname())
lock = threading.Lock()
C_F = os.path.join(conf.ssl_dir, conf.master_certfile)
K_F = os.path.join(conf.ssl_dir, conf.master_keyfile)

def id_generator(size=32, chars=string.ascii_uppercase + string.digits):
   return ''.join(random.choice(chars) for x in range(size))

def fix_quotes(data):
   data = data.replace('\'', '\'\'')
   return data

def Log(msg):
   if __name__ == "__main__":
      now = dt.datetime.now()
      print "%s :: %s" %(now, msg)

def create_self_signed_cert(keyfile, certfile):
   # create a key pair
   k = crypto.PKey()
   k.generate_key(crypto.TYPE_RSA, 4096)

   # create a self-signed cert
   cert = crypto.X509()
   cert.get_subject().C = "AU"
   cert.get_subject().ST = "QLD"
   cert.get_subject().L = "Brisbane"
   cert.get_subject().O = "DS_Schedule Master"
   cert.get_subject().OU = "DS_Schedule Master"
   cert.get_subject().CN = socket.gethostname()
   cert.set_serial_number(1000)
   cert.gmtime_adj_notBefore(0)
   cert.gmtime_adj_notAfter(10*365*24*60*60)
   cert.set_issuer(cert.get_subject())
   cert.set_pubkey(k)
   cert.sign(k, 'sha256')

   open(certfile, "wt").write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
   open(keyfile, "wt").write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))

class SecureTCPServer(SocketServer.TCPServer):
    def __init__(self,
                 server_address,
                 RequestHandlerClass,
                 certfile,
                 keyfile,
                 bind_and_activate=True):
        SocketServer.ThreadingTCPServer.allow_reuse_address = True
        SocketServer.TCPServer.__init__(self, server_address, RequestHandlerClass, bind_and_activate)
        self.certfile = certfile
        self.keyfile = keyfile

    def get_request(self):
        newsocket, fromaddr = self.socket.accept()
        connstream = ssl.wrap_socket(newsocket,
                                 server_side=True,
                                 certfile = self.certfile,
                                 keyfile = self.keyfile)
        return connstream, fromaddr

class Secure_ThreadingTCPServer(SocketServer.ThreadingMixIn, SecureTCPServer): pass

class Heartbeats(dict):
   """Manage shared heartbeats dictionary with thread locking"""

   def __init__(self):
      super(Heartbeats, self).__init__()
      self._lock = threading.Lock()

   def __setitem__(self, key, value):
      """Create or update the dictionary entry for a client"""
      self._lock.acquire()
      super(Heartbeats, self).__setitem__(key, value)
      self._lock.release()

   def getActive(self):
      """Return a list of clients with heartbeat older than conf.CHECK_TIMEOUT"""
      limit = time.time() - conf.CHECK_TIMEOUT
      self._lock.acquire()

      # We always consider ourselves up
      conf.peers[myself] = True

      inactive = [ip for (ip, ipTime) in self.items() if ipTime < limit]
      active = [ip for (ip, ipTime) in self.items() if ipTime >= limit]
      for peer in inactive:
         conf.peers[peer] = False
      for peer in active:
         conf.peers[peer] = True
      self._lock.release()
      return inactive

class Receiver(threading.Thread):
   """Receive UDP packets and log them in the heartbeats dictionary"""

   def __init__(self, goOnEvent, heartbeats):
      super(Receiver, self).__init__()
      self.goOnEvent = goOnEvent
      self.heartbeats = heartbeats
      self.recSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      self.recSocket.settimeout(conf.CHECK_TIMEOUT)
      self.recSocket.bind((myself, conf.PORT))

   def run(self):
      while self.goOnEvent.isSet():
         try:
            data, addr = self.recSocket.recvfrom(5)
            if data == 'PyHB':
               self.heartbeats[addr[0]] = time.time()
         except socket.timeout:
            pass

class Sender(threading.Thread):
   """Send Heartbeats to our peers"""
   def __init__(self, goOnEvent):
      super(Sender, self).__init__()
      self.goOnEvent = goOnEvent

   def run(self):
      while self.goOnEvent.isSet():
         for peer in conf.peers.keys():
            if peer != myself:
               hbSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
               hbSocket.sendto('PyHB', (peer, conf.PORT))
         time.sleep(conf.CHECK_TIMEOUT)

class Event_Receiver(SocketServer.BaseRequestHandler):
   def setup(self):
      print self.client_address, 'connected to event engine!'

   def handle(self):
      util = Util()
      ev_in = self.connection.recv(1024)
      event = cPickle.loads(ev_in)
      e_type = event[0]
      host = event[1]
      path = event[2]
      filename = event[3]
      Log("Received %s event for host %s : file %s" % (e_type, host, filename))
      util.runQuery("update jobs j, event_table e set j.update_flag=1 where j.event_trigger=e.id and  e.event_type='%s' and e.host='%s' and target='%s'" % (e_type, host, path))

class EventEngine(threading.Thread):
   def run(self):
      global C_F
      global K_F
      #This 'event_engine' is for the remote trigger events.
      server = Secure_ThreadingTCPServer(('', conf.event_port), Event_Receiver, C_F, K_F)
      # Start a thread with the server -- that thread will then start one more thread for each request
      Log("Started Event engine.")
      server.serve_forever()

   def shutdown(self):
      Log("Shutting down event engine")
      self._Thread__stop()

class DB:
   """ Database Handler """
   def __init__(self):
      conn = None

   def connect(self):
      try:
         self.conn = MySQLdb.connect(host=conf.dbconfig['dbhost'],
                     user=conf.dbconfig['dbuser'],
                     passwd=conf.dbconfig['dbpass'],
                     db=conf.dbconfig['dbname'])
      except (AttributeError, MySQLdb.OperationalError):
         print("Database Connection failed, retrying...")
         time.sleep(2)
         self.connect()
      finally:
         Log("Database connected.")

   def query(self, sql):
      try:
         cursor = self.conn.cursor()
         cursor.execute(sql)
      except (AttributeError, MySQLdb.OperationalError):
         self.connect()
         cursor = self.conn.cursor()
         cursor.execute(sql)
      return cursor

#Utility Class
class Util:
   """ Utility functions for the Scheduler """
   db = DB()

   def runQuery(self, query):
      lock.acquire()
      try:
         curs = self.db.query(query)
      except MySQLdb.IntegrityError:
         return None
      finally:
         lock.release()
      result = curs.fetchall()
      return result

   def init_path(self):
      if not os.path.isfile(conf.logfile):
         os.system('touch %s' % (conf.logfile))

   def init_DB(self):
      current_db_version = 4
      # Most useful on initial install, but should repair any damaged tables.
      #self.runQuery("")
      self.runQuery("CREATE TABLE IF NOT EXISTS dbversion ( id int(11) NOT NULL, db_version int(11) NOT NULL, PRIMARY KEY (id)) ENGINE=MyISAM DEFAULT CHARSET=latin1")
      self.runQuery("INSERT INTO dbversion (id, db_version) VALUES (0, 1)")
      self.runQuery("CREATE TABLE IF NOT EXISTS dep_modes ( mode_id int(11) NOT NULL, mode varchar(25) NOT NULL, PRIMARY KEY (mode_id)) ENGINE=MyISAM DEFAULT CHARSET=latin1")
      self.runQuery("INSERT INTO dep_modes (mode_id, mode) VALUES (0, 'ON_SUCCESS'), (1, 'ON_FAILURE'), (2, 'ON_KILL')")
      self.runQuery("CREATE TABLE IF NOT EXISTS event_table ( id int(11) NOT NULL AUTO_INCREMENT, event_type varchar(30) NOT NULL, target varchar(255) NOT NULL, host varchar(30) NOT NULL DEFAULT 'localhost', update_flag int(11) NOT NULL DEFAULT 1, condition_met int(11) NOT NULL DEFAULT 0, PRIMARY KEY (id)) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=2 ")
      self.runQuery("CREATE TABLE IF NOT EXISTS jobs ( id int(11) NOT NULL AUTO_INCREMENT, name varchar(255) NOT NULL, host varchar(30) NOT NULL, user varchar(31) NOT NULL, start_time datetime DEFAULT NULL, end_time datetime DEFAULT NULL, depends int(11) NOT NULL DEFAULT 0, depend_mode int(11) NOT NULL DEFAULT 0, event_trigger int(11) NOT NULL DEFAULT 0, reoccur varchar(30) DEFAULT NULL, status int(11) NOT NULL DEFAULT 99999, rc int(11) DEFAULT 99999, command varchar(300) NOT NULL, update_flag tinyint(1) NOT NULL DEFAULT 1, comment text NOT NULL, PRIMARY KEY (id), UNIQUE KEY dedup_jobs (name,host)) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=29 ")
      self.runQuery("CREATE TABLE IF NOT EXISTS results ( id int(11) NOT NULL, start_date datetime DEFAULT NULL, end_date datetime DEFAULT NULL, output text, uid varchar(32) NOT NULL, KEY id (id), rc int(11) NOT NULL) ENGINE=MyISAM DEFAULT CHARSET=latin1")
      self.runQuery("INSERT INTO jobs (id, name, host, user, start_time, end_time, depends, depend_mode, event_trigger, reoccur, status, rc, command, update_flag, comment) VALUES (0, 'Scheduler Maintenance', 'localhost', 'root', NULL, NULL, 0, 0, 0, '0 0 * * *', 99999, 99999, '/opt/scheduler/sched_db_maintenance.py', 0, 'Internal DS SCheduler jobs. Do not remove. ')")

     # Ok, Now let's upgrade the database from previous versions
      db_version = self.runQuery("SELECT db_version from dbversion limit 1")[0][0]
      Log("Database version : %i" % (db_version))
      while db_version < current_db_version:
         if db_version == 1:
            Log("Updating database to version 2")
            self.runQuery("ALTER TABLE jobs ADD log_retention INT( 11 ) NOT NULL DEFAULT '30'")
            self.runQuery("UPDATE dbversion set db_version=2")
            db_version = 2
         if db_version == 2:
            Log("Updating database to version 3")
            self.runQuery("ALTER TABLE jobs ADD pid INT( 11 ) NULL")
            self.runQuery("UPDATE dbversion set db_version=3")
            db_version = 3
         if db_version == 3:
            Log("Updating database to version 4")
            self.runQuery("ALTER TABLE jobs CHANGE user user VARCHAR( 31 ) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL ")
            self.runQuery("UPDATE dbversion set db_version=4")
            db_version = 4

   def refresh_jobs(self):
      jobs = {}
      job_query = self.runQuery("SELECT * FROM jobs a LEFT OUTER JOIN dep_modes b ON a.depend_mode = b.mode_id")
      for j in job_query:
         jobs[j[1]] = j
      return jobs

   def refresh_events(self):
      events = {}
      eve_query = self.runQuery("SELECT * FROM event_table")
      for j in eve_query:
         events[j[1]] = j
      return events

   def remote_command(self, job_id, host, cmd, user, job_name):
      # Check if previous job is still markes as running. It may be faulty or stuck.
      run_status = self.runQuery("select status, pid from jobs where id='%s'" % (job_id))[0]
      if run_status == '99998':
         # Previous job is still running. We should try to kill it. 
         # TODO: Send an alert
         cmd = 'kill -9 %s' % (run_status[1])

      #If the agent cert doesn't exist yet retreive it. Otherwise reject it as this may be a rouge connection
      agent_certfile = os.path.join(conf.agent_certs, '%s.pem' % (host))
      if not os.path.exists(agent_certfile):
         Log("Missing cert for %s, retrieveing cert." % (host))
         servercert = ssl.get_server_certificate((host, conf.agent_port))
         if servercert:
            e = open(agent_certfile, 'w')
            e.write(servercert)
            e.close()
         else:
            # We failed to get the agent SSL cert, so bail.
            Log("Cert verification failed for %s:" % (host))
            self.runQuery("update jobs set end_time=now(), rc=99994, status=99994 where id='%s'" % (job_id)) # Error
            self.runErrorCommand(job_name, 99994)
            return None

      unique_id = id_generator()
      if cmd.startswith('kill'):
         Log("Killing job %s on host %s" % (job_name, host))
      else:
         Log("Running job %s on host %s" % (job_name, host))
      client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      ssl_socket = ssl.wrap_socket(client_socket, ca_certs=agent_certfile, cert_reqs=ssl.CERT_REQUIRED)
      try:
         ssl_socket.connect((host, conf.agent_port))
      except:
         #[Errno 113] No route to host or agent is offline. Let's flag that.
         Log("Job %s Failed:" % (job_id))
         self.runQuery("update jobs set end_time=now(), rc=99994, status=99994 where id='%s'" % (job_id)) # Error
         self.runErrorCommand(job_name, 99994)
         return None
      command = cPickle.dumps([cmd, user])
      ssl_socket.send(command)
      if cmd.startswith('ON_'):
         return None
      # Lets get the PID so that we can manage the process.
      rawdata = ssl_socket.recv(10240)
      try:
         data = cPickle.loads(rawdata)
      except UnpicklingError:
         output = 'Error receiving PID from slave.'
      finally:
         pid = data[0]

      if not cmd.startswith('kill'):
         self.runQuery("update jobs set start_time=now(),status=99998, pid=%s where id=%s" % (pid, job_id))
         self.runQuery("insert into results VALUES(%s, now(), NULL, NULL, '%s', 99999)" % (job_id, unique_id))

      rawdata = ssl_socket.recv(10240)

      try:
         data = cPickle.loads(rawdata)
      except UnpicklingError:
         output = 'Error receiving data from slave. Possibly too much output?'
      finally:
         rc = data[0]

      if not cmd.startswith('kill'):
         Log("Job id %s returned with %s" % (job_id, rc))
         output=fix_quotes(data[1])
         if rc > 0:
            Log("Run error command with parameters: %s %s" % (job_name, rc))
            self.runErrorCommand(job_name, rc)
         if rc == 126:
            output = 'Command invoked cannot execute.'
         if rc == 127:
            output = 'Command not found.'
         if rc == 128:
            output = 'Exit code above 255.'
         if rc == 137:
            output = 'Process Killed.'
            self.runQuery("update jobs set rc=%s, status=99996, end_time=now() where id=%s" % (rc, job_id))
         else:
            self.runQuery("update jobs set rc=%s, status=99999, end_time=now(), pid=0 where id=%s" % (rc, job_id))

         self.runQuery("update results set end_date=now(), output='%s', rc=%s where uid='%s'" % (output, rc, unique_id))
         # wake up any job that depends on the current one finishing
         self.runQuery("update jobs set update_flag=1 where depends='%s'" % (job_id))
         return data
      # We have attempted a kill command, we may have to handle it here if the parent connection died.
      else:
         if rc == 0:
            pass
         if rc == 1:
            pass

   def remove_job(self, job_id):
      self.runQuery("delete from jobs where id='%s'" % (job_id))

   def disable_job(self, job_id):
      self.runQuery("update jobs set update_flag=0, status=99997 where id='%s'" % (job_id))

   def reset_job(self, job_id):
      self.runQuery("update jobs set update_flag=1, rc=99999, status=99999 where id='%s'" % (job_id))

   def reset_all(self):
      # Set all flags for the first timeDA or on failover.
      Log("Setting update flags")
      self.runQuery("update jobs set update_flag=1, event_trigger=0, rc=99999, status=99999, pid=0 where status != 99997")
      self.runQuery("update event_table set update_flag=1, condition_met=0")

   def job_status(self, job_id):
      job = self.runQuery("select * from jobs where id=%s" % (job_id))[0]
      if job:
         return job

   def runErrorCommand(self, job_name, rc):
      if conf.command_jobfail:
         os.system(conf.command_jobfail % (job_name, rc)) # call error script

class DS_Scheduler:
   """ The main guts and logic for the scheduler."""
   def __init__(self):
      self.util = Util()
      self.sched = Scheduler(conf.config)
      self.sched.start()
      self.queue = {}
      self.util.init_path()
      self.util.init_DB()
      self.util.reset_all()

   def run(self):
      # Main Loop
      i = 0
      master = False
      idle = False
      while True:
         if conf.clustering == True:
            inactive = heartbeats.getActive()
            ''' Here is where we elect our current master node. If the conf.preferred_master
                is not us and is not up yet (Neither True or False), then we will wait 10 check cycles
                and if the master is not up we will assume control. '''
            if conf.preferred_master == myself:
               # I am the master node and I should alwas be in charge
               master = True
               i = 0
            elif conf.preferred_master != myself and conf.peers[conf.preferred_master] == 'True':
               # The master will take control now
               master = False
            elif conf.peers[conf.preferred_master] == False:
               # Assume the master server is dead
               master = True
            elif conf.peers[conf.preferred_master] == '':
               # Master has not been started yet
               i += 1
               if i >= 10:
                  master = True
                  i = 10
            else:
               # I am not the master node, but I am available just in case
               master = False
         if master == True or conf.clustering == False:
            idle = False
            events = self.util.refresh_events()
            for e in events.keys():
               event = events[e]
               e_id = event[0]
               e_type = event[1]
               e_target = event[2]
               e_host = event[3]
               e_update_flag = event[4]
               if e_update_flag == 1:
                  self.util.remote_command(e_id, e_host, e_type, e_target, 'NEW EVENT')
                  self.util.runQuery("update event_table set update_flag=0 where id=%s" % (e_id))

            jobs = self.util.refresh_jobs()
            for j in jobs.keys():
               job = jobs[j]
               # IF the job was updated then the update_flag will be set, so reschedule
               # TODO: Change these in the code below
               j_id = job[0]
               j_name = job[1]
               j_host = job[2]
               j_user = job[3]
               j_dep = job[6]
               j_etrigger = job[8]
               j_cron = job[9]
               j_command = job[12]
               j_update_flag = job[13]
               j_pid = job[16]
               j_dep_mode = job[17]
               job_name = '%s_%i' % (j_name, j_id)
               now = dt.datetime.now() + dt.timedelta(seconds=5)
               if j_update_flag == 1:
                  # Lets make sure the job does not already exist. If it does it means the user had edited an existing job so let's requeue
                  try:
                     self.sched.unschedule_job(self.queue[job_name])
                     # Remove job from queue
                     self.queue.pop(job_name)
                     Log("Refreshing job %s" %(job_name))
                  except(KeyError):
                     pass

                  # DEP SECTION
                  if j_etrigger > 0: # Event trigger
                     # immediate jobs like event jobs and run_now jobs need not collide with the namespace
                     # of cron jobs. So lets randomize the name
                     current_job = self.sched.add_date_job(self.util.remote_command, now, name=job_name, args=(j_id, j_host, j_command, j_user, job_name))
                     Log(current_job)
                     self.util.runQuery("UPDATE jobs set update_flag=1, event_trigger=0 where id='%s'" % (j_id))
                  if j_dep > 0: # If job depends on another...
                     now = dt.datetime.now() + dt.timedelta(seconds=10)
                     parent = self.util.job_status(j_dep)
                     if j_dep_mode == 0  and j_dep_mode == parent[11]:  # ON_SUCCESS
                        current_job = self.sched.add_date_job(self.util.remote_command, now, name=job_name, args=(j_id, j_host, j_command, j_user, job_name))
                        Log(current_job)
                     if j_dep_mode == 1 and j_dep_mode == parent[11]:  # ON_FAIL
                        current_job = self.sched.add_date_job(self.util.remote_command, now, name=job_name, args=(j_id, j_host, j_command, j_user, job_name))
                        Log(current_job)
                     if j_dep_mode == 2 and j_dep_mode == parent[11]:  # ON_KILL
                        current_job = self.sched.add_date_job(self.util.remote_command, now, name=job_name, args=(j_id, j_host, j_command, j_user, job_name))
                        Log(current_job)
                     self.util.runQuery("update jobs set update_flag=0 where id='%s'" % (j_id))
                  if j_etrigger == 0 and j_dep == 0:  #Standard "cron" type scheduling
                     crontab = j_cron.split()
                     # Job Names need to be unique, so the same 'job' being run on different hosts can work.
                     current_job = self.sched.add_cron_job(self.util.remote_command,
                                                          minute=crontab[0],
                                                          hour=crontab[1],
                                                          day=crontab[2],
                                                          month=crontab[3],
                                                          day_of_week=crontab[4],
                                                          name=job_name,
                                                          args=(j_id, j_host, j_command, j_user, job_name),
                                                          max_instances=2)

                     # Add the job to the queue
                     Log(current_job)
                     self.queue[job_name] = current_job
                     self.util.runQuery("update jobs set update_flag=0 where id='%s'" % (j_id))
               # Job was marked for removal
               if j_update_flag == 2:
                  self.sched.unschedule_job(self.queue[job_name])
                  # Remove job from queue
                  self.queue.pop(job_name)
                  self.util.remove_job(j_id)
                  Log("Unscheduled job %s" %(job_name))
                  self.util.runQuery("update jobs set update_flag=0 where id='%s'" % (j_id))
               if j_update_flag == 3:
                  Log("Disabling Job: %s" % (job_name))
                  self.sched.unschedule_job(self.queue[job_name])
                  # Remove job from queue
                  self.queue.pop(job_name)
                  self.util.disable_job(j_id)
                  #self.util.runQuery("update jobs set update_flag=0 where id='%s'" % (j_id))
               if j_update_flag == 4:
                  Log("Killing PID: %s   Job: %s" % (j_pid, job_name))
                  kill_command = 'kill -9 %s' % (j_pid)
                  current_job = self.sched.add_date_job(self.util.remote_command, now, name='ON_KILL %s' % (j_pid), args=(j_id, j_host, kill_command , j_user, job_name))
                  Log(current_job)
                  self.queue[job_name] = current_job
                  self.util.runQuery("update jobs set update_flag=0, status=99996 where id='%s'" % (j_id))
            #pprint(self.queue)
            time.sleep(conf.CHECK_PERIOD)
         else:
            # Unscheduling all jobs so that the peer node can take over.
            if idle == False:
               jobs = self.util.refresh_jobs()
               for j in jobs.keys():
                  job = jobs[j]
                  self.sched.unschedule_job(self.queue[job_name])
                  # Remove job from queue
                  self.queue.pop(job_name)
                  Log("Failed over job %s" %(job_name))
               self.util.reset_all_jobs()
               idle = True

      self.sched.shutdown()

def main():
   global C_F
   global K_F

   # Generate a cert for the master if we do not have one yet.
   if not os.path.exists(conf.ssl_dir):
      os.mkdir(conf.ssl_dir, 0700)
   # Make the dir for the agent certs.
   if not os.path.exists(conf.agent_certs):
      os.mkdir(conf.agent_certs)

   if not os.path.exists(C_F) or not os.path.exists(K_F):
      create_self_signed_cert(K_F, C_F)

   os.umask(077)
   if conf.clustering == True:
      #This 'Event' is for Cluster heartbeats
      Event = threading.Event()
      Event.set()
      heartbeats = Heartbeats()
      receiver = Receiver(goOnEvent = Event, heartbeats = heartbeats)
      receiver.start()
      sender = Sender(goOnEvent = Event)
      sender.start()

   event_engine = EventEngine()
   event_engine.start()

   try:
      app = DS_Scheduler()
      app.run()
   except (KeyboardInterrupt):
      Log("Shutting Down")
      event_engine.shutdown()
      #server.shutdown()

if __name__ == "__main__":
   main()
