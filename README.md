_______________________________________________________________________________
                   DS Scheduler
_______________________________________________________________________________
A centralized 'cron' type scheduling system for UNIX/Linux. It has a web 
interface for managing, monitoring and scheduling jobs and commands in a 
multi-host environment. Can execute jobs based on event triggers. Secure
communications between master servers and clients. Clusterable: Master can 
automatically fail over so any number of secondary masters. Ajax web interface 
for better monitoring and execution feedback. Graphing/Reporting: Visualize 
the running duration and timing of your jobs.


Releases are alavilable in tar.bz2 format:

https://solar1.net/files/scheduler-0.7tar.bz2

Features:

    Can be used as a drop-in replacement for cron.
    Can execute jobs based on event triggers.
    Secure communications between master servers and clients.
    Cluster-able: Master can automatically fail over to any number of secondary masters. 
    Ajax web interface for better monitoring and execution feedback.
    Graphing/Reporting: Visualize the running duration and timing of your jobs.
    Run Jobs based on File Triggers
    Database will upgrade itself.
    Web interface will indicate if the master is running or not.

 
Installation:
Requirements:

 - APSchedler - available at http://packages.python.org/APScheduler

 - Apache Web server

 - Python >= 2.6

Point your web server to the 'web' directory that is under scheduler/.  If you installed in /opt/scheduler, then an example apache entry would be:

Alias /scheduler/ /opt/scheduler/web/
<Directory /opt/scheduler/web/>
   AuthType Basic
   AuthName "DS_SChed"
   AuthUserFile /opt/scheduler/.htpasswd
   require valid-user
</Directory>

Secure your site by using SSL and htpasswd. You can run root processes with the scheduler to restricting access is highly recommended.  

Creating an htpasswd file:

htpasswd -c /opt/scheduler/.htpasswd <user>

Contributing

 - Fork it
 - Create your feature branch (git checkout -b my-new-feature)
 - Commit your changes (git commit -am 'Add some feature')
 - Push to the branch (git push origin my-new-feature)
 - Create new Pull Request
