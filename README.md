_______________________________________________________________________________
<h1>                   DS Scheduler</h1>
_______________________________________________________________________________
A centralized 'cron' type scheduling system for UNIX/Linux. It has a web
interface for managing, monitoring and scheduling jobs and commands in a
multi-host environment. Can execute jobs based on event triggers. Secure
communications between master servers and clients. Clusterable: Master can
automatically fail over so any number of secondary masters. Ajax web interface
for better monitoring and execution feedback. Graphing/Reporting: Visualize
the running duration and timing of your jobs.


<h1>Features:</h1>

 - Can be used as a drop-in replacement for cron.
 - Can execute jobs based on event triggers.
 - Secure communications between master servers and clients.
 - Cluster-able: Master can automatically fail over to any number of secondary masters.
 - Ajax web interface for better monitoring and execution feedback.
 - Graphing/Reporting: Visualize the running duration and timing of your jobs.
 - Run Jobs based on File Triggers
 - Database will upgrade itself.
 - Web interface will indicate if the master is running or not.


<h1>Installation:</h1>
<h2>Requirements:</h2>

 - APSchedler - available at http://packages.python.org/APScheduler

 - Apache Web server

 - Python >= 2.6

Point your web server to the 'web' directory that is under scheduler/.  If you installed in /opt/scheduler, then an example apache entry would be:

'''
Alias /scheduler/ /opt/scheduler/web/
<Directory /opt/scheduler/web/>
   AuthType Basic
   AuthName "DS_SChed"
   AuthUserFile /opt/scheduler/.htpasswd
   require valid-user
</Directory>
'''

Secure your site by using SSL and htpasswd. You can run root processes with the scheduler to restricting access is highly recommended. 

<h3>Creating an htpasswd file:</h3>

htpasswd -c /opt/scheduler/.htpasswd <user>

<h3>Create the Database</h3>

Create a mysql user and a blank DB in MySQL. Make sure to update the sched_config.py and the dbconfig.php files to reflect the database user, host, and passwd.
Note for version 0.5 and later:

The sched_master application will create and upgrade the database tables. The goal here it to avoid doing any DB maintenance to allow for very easy upgrades.

Screenshots:
Web interface:

Graphs:


Admin Console (New in 0.7):


Those that prefer the Command Line will be happy that I am working on a terminal based console for DS-scheduler. Just run sched_console:

Hit the H key to bring up the key commands.
Sched_admin (New in 0.7):

Managing jobs are easy to script now with this command line interface:

Usage: sched_admin [OPTIONS]

Options:
 -h , --help         Print this info
 -l, --list          List jobs in the system
 -r, --run [ id ]    Run job id immediately
 -k, --kill [ id ]   Kill running job
 -a, --add [ id ]    Add a new job
     --cron <cron notation> --name <name> --host <host> --user <user> --depends [ id ] --mode [ ON_SUCCESS | ON_FAILURE ]
 -d, --delete [ id ] Delete job completely
 -e, --enable [ id ] Enable a disabled job
 -x, --disable [ id ] Disable job from running
 -q, --quiet         Quiet mode ( good for scripting )

TO DO:

    Not every feature on the web interface works yet. Anyone who knows web development could probably do better. Patches are welcome. Update: Most web features now work. Testing needed.
    Need to add ON_NEWFILE trigger.  Done
    Need to add ON_FILECHANGE trigger.
    Need better reporting/graphing flexibility.
    Need Translations

Database:

For those who want to contribute to the development, Here is an outline of the database:

Table:  Jobs
<table>
<tr><td>id</td><td>int(11)</td><td>AUTO_INCREMENT     unique job ID</td></tr>
name          varchar(255)   Human readable job name
host          varchar(30)    Host that job will run on
user          varchar(10)    user that job will run as
start_time    datetime       The last time the job started
end_time      datetime       The last tim the job ended
depends       int(11)        Does this job depend on another?
depend_mode   int(11)        See the dep_mode table
reoccur       varchar(30)    'cron' type notation
status        int(11)        The running status
rc            int(11)        The exit code of the job
command       varchar(300)   The actual command to run
update_flag   tinyint(1)     Trigger the scheduler to re-read the job
comment       text           Human readable comments
Log_Retention int            How long in days to keep run logs

Table:  dep_mode

For managing dependant modes

mode_id       int(11)        Unique ID
mode          varchar(25)    Description of mode (i.e. ON_FAILURE)

Table: Results

For storing output and times for reporting

id            int(11)        Unique ID
start_date    datetime       Time the job started
end_date      datetime       Time the job exited
output        text           Command/Job output text
uid           varchar(32)    Unique identifier for each job instance

Table: Events


Table: db_version

This table is for keeping track of the database structure.


id int(11)
db_version int(11)

<h1>Contributing</h1>

 - Fork it
 - Create your feature branch (git checkout -b my-new-feature)
 - Commit your changes (git commit -am 'Add some feature')
 - Push to the branch (git push origin my-new-feature)
 - Create new Pull Request
