<?php

ini_set("display_errors",1);
error_reporting(E_ALL ^E_NOTICE);

$logfile = "/var/log/scheduler_web.log";

$core = './xajax/xajax_core';
require_once 'dbconfig.php';
include ( "jpgraph/src/jpgraph.php");
include ("jpgraph/src/jpgraph_gantt.php");
require_once $core . '/xajax.inc.php';

$xajax = new xajax($siteurl);

// Sqlite3
//$db = new PDO('sqlite:../service_state.db');
// MySql 5
$db = new PDO("mysql:host={$dbserver};dbname={$database}", $username, $password);
$xajax->configure("javascript URI","xajax/");
$xajax->configure("responseQueueSize","50000");
$xajax->register(XAJAX_FUNCTION,"watchList");
$xajax->register(XAJAX_FUNCTION,"removejob");
$xajax->register(XAJAX_FUNCTION,"disablejob");
$xajax->register(XAJAX_FUNCTION,"enablejob");
$xajax->register(XAJAX_FUNCTION,"resetjob");
$xajax->register(XAJAX_FUNCTION,"killjob");
$xajax->register(XAJAX_FUNCTION,"Action");
$xajax->register(XAJAX_FUNCTION,"show");
//$xajax->configure("debug", true);
$xajax->processRequest();

function watchList()
{
   $objResponse = new xajaxResponse();
   global $db;

   exec("pgrep -f \"python.*sched_master\"", $pids);
   if(empty($pids)) 
   {
      $objResponse->assign("master_daemon_status", "innerHTML", "MASTER OFFLINE");
      $objResponse->assign("master_daemon_status", "style.background", "#FF7D7D");
   }
   else
   {
      $objResponse->assign("master_daemon_status", "innerHTML", "MASTER ONLINE");
      $objResponse->assign("master_daemon_status", "style.background", "#CFFFAB");
   }
   foreach ($db->query("SELECT * FROM jobs LEFT OUTER JOIN dep_modes ON jobs.depend_mode = dep_modes.mode_id") as $jobs)
   {
      $id = $jobs[id];
      if ($jobs[status] != 99997)
         $objResponse->assign("enable_disable_{$id}", "innerHTML", "<a onclick=\"xajax_disablejob('{$jobs[id]}');\" class=\"ui-state-default ui-corner-all\">Disable</a>");
      else
         $objResponse->assign("enable_disable_{$id}", "innerHTML", "<a onclick=\"xajax_enablejob('{$jobs[id]}');\" class=\"ui-state-default ui-corner-all\">Enable</a>");

      $objResponse->assign("start_time_{$id}", "innerHTML", "{$jobs[start_time]}");
      $objResponse->assign("end_time_{$id}", "innerHTML", "{$jobs[end_time]}");
      $objResponse->assign("depend_{$id}", "innerHTML", "{$jobs[depends]}");
      $objResponse->assign("depend_mode_{$id}", "innerHTML", "{$jobs[mode]}");
      $objResponse->assign("reoccur_{$id}", "innerHTML", "{$jobs[reoccur]}");
      if ($jobs[pid] == 0)
      {
         $objResponse->assign("pid_{$id}", "innerHTML", "");
      }
      else
      {
         $objResponse->assign("pid_{$id}", "innerHTML", "{$jobs[pid]}");
      }
      switch($jobs[rc])
      {
         case 0:
            $objResponse->assign("rc_{$id}", "innerHTML", "SUCCESS");
            $objResponse->assign("rc_{$id}", "style.background", "#CFFFAB");
            break;
         case -9:
         case 137:
            $objResponse->assign("rc_{$id}", "innerHTML", "KILLED");
            $objResponse->assign("rc_{$id}", "style.background", "#FF7D7D");
            break;
         case 99999:
            $objResponse->assign("rc_{$id}", "innerHTML", "UNKNOWN");
            $objResponse->assign("rc_{$id}", "style.background", "#AEAEAE");
            break;
         case 99994:
            $objResponse->assign("rc_{$id}", "innerHTML", "OFFLINE");
            $objResponse->assign("rc_{$id}", "style.background", "#FF7D7D");
            break;
         default:
            $objResponse->assign("rc_{$id}", "innerHTML", "FAILED");
            $objResponse->assign("rc_{$id}", "style.background", "#FF7D7D");
            break;
      }

      switch($jobs[status])
      {
         case 0:
            $objResponse->assign("status_{$id}", "innerHTML", "DONE");
            $objResponse->assign("status_{$id}", "style.background", "#CFFFAB");
            break;
         case 99999:
            $objResponse->assign("status_{$id}", "innerHTML", "PENDING");
            $objResponse->assign("status_{$id}", "style.background", "#FFFFFF");
            break;
         case 99998:
            $objResponse->assign("status_{$id}", "innerHTML", "RUNNING");
            $objResponse->assign("status_{$id}", "style.background", "#ABD9FF");
            break;
         case 99997:
            $objResponse->assign("status_{$id}", "innerHTML", "DISABLED");
            $objResponse->assign("status_{$id}", "style.background", "#8D8D8D");
            break;
         case 99996:
            $objResponse->assign("status_{$id}", "innerHTML", "KILLED");
            $objResponse->assign("status_{$id}", "style.background", "#FF7D7D");
            break;
         case 99994:
            $objResponse->assign("status_{$id}", "innerHTML", "OFFLINE");
            $objResponse->assign("status_{$id}", "style.background", "#FF7D7D");
            break;
         default:
            $objResponse->assign("status_{$id}", "innerHTML", "UNKNOWN");
            $objResponse->assign("status_{$id}", "style.background", "#AEAEAE");
            break;
      }
   }
   return $objResponse;
}

function show($name)
{
   $objResponse = new xajaxResponse();
   $objResponse->assign("${name}", "style.display", "");
   return $objResponse;
}

function viewJobs()
{
   global $db;

   $content = "<table width=\"100%\">
  <thead>
   <tr>
      <th></th><!-- <th>Job ID</th> --><th>Host</th><th>Name</th><th>Run As User</th><th>Last Start Time</th><th>Last End Time</th><th>Depends</th><th>Dependancy Mode</th><th>Reocurring</th><th>Last Run</th><th>Status</th><th>PID</th><th>Run Log</th>
   </tr>
  </thead>
  <tbody>";
   $i = 0;
   foreach ($db->query("SELECT a.id, a.name as name, a.host, a.user, b.name as dep FROM jobs a LEFT OUTER JOIN jobs b ON a.depends = b.id") as $jobs)
   {

      if ($i == 0)
      {
         $class = "class=\"roweven\"";
         $i++;
      }
      else
      {
         $class = "class=\"rowodd\"";
         $i = 0;
      }

      $content .= "<tr {$class}>
                     <td align=\"center\"><input name=\"selected_job[]\" value=\"{$jobs[id]}\" type=\"checkbox\"></td>
                     <!-- <td>{$jobs[id]}</td> -->
                     <td><div><p><a href=\"#\" id=\"edit_link_{$jobs[id]}\" class=\"ui-state-default ui-corner-all\">{$jobs[name]}</a></p></div></td>
                     <td>{$jobs[host]}</td>
                     <td>{$jobs[user]}</td>
                     <td><div id=\"start_time_{$jobs[id]}\"></div></td>
                     <td><div id=\"end_time_{$jobs[id]}\"></div></td>
                     <td><div id=\"depends_{$jobs[id]}\">{$jobs[dep]}</div></td>
                     <td><div id=\"depend_mode_{$jobs[id]}\"></div></td>
                     <td><div id=\"reoccur_{$jobs[id]}\"></div></td>
                     <td><div id=\"rc_{$jobs[id]}\"></div></td>
                     <td><div id=\"status_{$jobs[id]}\"></div></td>
                     <td><div id=\"pid_{$jobs[id]}\"></div></td>
                     <td><a href=\"log.php?id={$jobs[id]}\">Log</a></td>
                  </tr>";
   }
   $content .= "</tbody>\n</table>\n";

   foreach ($db->query("select * from jobs") as $jobs)
   {
      $content .= "<div id=\"edit_dialog_{$jobs[id]}\" title=\"{$jobs[name]}\"></div>";
   }

   return $content;
}

function dialogs_js()
{
   global $db;
   $content="";
   foreach ($db->query("select id from jobs") as $jobs)
   {
      $content .= "            $('#edit_dialog_{$jobs[id]}').dialog({autoOpen: false, resizable: false, position: 'center', stack: true, height: 'auto', width: 'auto', modal: true });\n";
      $content .= "            $('#edit_link_{$jobs[id]}').click(function(){ $.ajax({ type: 'get', dataType: 'html', url: 'edit_dialog.php?id={$jobs[id]}', data: {}, success: function(response) { $(\"#edit_dialog_{$jobs[id]}\").empty().html(response).dialog('open'); } }) });\n";
   }
   return $content;
}

function editJobDialog()
{
   $content = "<div id=\"add_dialog\" title=\"Schedule New Job\">
   <form method=\"post\" action=\"add.php\" name=\"add_job\">
      <table>
         <tr>
            <td>Name <input name=\"name\" class=\"sminput\"></td>
            <td>Host <input name=\"host\" class=\"sminput\"></td>
         </tr>
         <tr>
            <td>User <input name=\"user\" class=\"sminput\"></td>
            <td>Start Time <input name=\"start_time\" class=\"sminput\"></td>
         </tr>
         <tr>
            <td>Fails After <input name=\"end_time\" class=\"sminput\"></td>
            <td>Depend_times <input name=\"depends\" class=\"sminput\"></td>
         </tr>
         <tr>
            <td>Cron schedule <input name=\"cron\" class=\"sminput\"> </td>
            <td>Command <input name=\"cmd\" class=\"sminput\"> </td>
         </tr>
      </table>
   </form>
</div>";

return $content;
}

/*
$aFormValues)
{
        $host = $aFormValues['host'];
*/

function Action($aFormValues, $action)
{
   $jobs = $aFormValues['selected_job'];
   global $db;
   foreach($jobs as $id)
   {
      switch($action)
      {
      case 'run_now':
         $db->exec("update jobs set update_flag=1, event_trigger=1, rc=99999 where id=${id}");
         Logit("Running Job ${id}");
         break;
      case 'kill':
         $db->exec("update jobs set update_flag=4 where id=${id}");
         Logit("Killing Job ${id}");
         break;
      case 'remove':
         $db->exec("update jobs set update_flag=2 where id=${id}");
         Logit("Deleting Job ${id}");
         echo "<meta http-equiv='refresh' content='0;URL=index.php'>";
         break;
      case 'disable':
         $db->exec("update jobs set update_flag=3 where id=${id}");
         Logit("Disabling Job ${id}");
         break;
      case 'enable':
         $db->exec("update jobs set update_flag=1, rc=99999 where id=${id}");
         Logit("Enabling Job ${id}");
         break;
      case 'reset':
         $db->exec("update jobs set update_flag=1, event_trigger=0, start_time=NULL, end_time=NULL, rc=99999 where id=${id}");
         Logit("Ressing Job ${id}");
         break;
      }
   }

}

function getJobspulldown($default)
{
   global $db;
   $content = "";
   foreach ($db->query("select id,name from jobs") as $jobs)
   {
      $content .= "<option value=\"{$jobs[id]}\" ";
      if ($default == $jobs[id])
         $content .="selected=\"selected\"";
      $content .= ">{$jobs[name]}</option>\n";
   }
   return $content;
}

function getModepulldown($default)
{
   global $db;
   $content = "";
   foreach ($db->query("select mode_id,mode from dep_modes") as $modes)
   {
      $content .= "<option value=\"{$modes[mode_id]}\" ";
      if ($default == $modes[mode_id])
         $content .="selected=\"selected\"";
      $content .= ">{$modes[mode]}</option>\n";
   }
   return $content;
}

function Logit($msg)
{
global $logfile;
// open file
$fd = fopen($logfile, "a");
// write string
fwrite($fd, $msg . "\n");
// close file
fclose($fd);
}

?>
