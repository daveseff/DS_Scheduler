<?php 
session_start();
$_SESSION['last_url'] = $_SERVER['REQUEST_URI']; 
include "functions.php";
?>
<!DOCTYPE html>
<html>
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />
  <title>DS Scheduler Web Console</title>
  <link rel="stylesheet" type="text/css" href="css/layout.css" />
  <link rel="stylesheet" type="text/css" href="css/menu_style.css" />
  <link type="text/css" href="css/smoothness/jquery-ui.css" rel="stylesheet" />
  <script type="text/javascript" src="js/jquery.js"></script>
  <script type="text/javascript" src="js/jquery-ui/jquery-ui.js"></script>
  <script type="text/javascript" src="js/funcs.js"></script>
  <?php $xajax->printJavaScript();?>
<script type="text/javascript">
/* <![CDATA[ */
function timer()
{
   xajax_watchList();
   window.setInterval("xajax_watchList();",5000);//reload timer
}
/* ]]> */
</script>
<script type="text/javascript">
$(function(){
   // Dialog and links
   <?php echo dialogs_js(); ?>

   // Add service Dialog
   $('#add_dialog').dialog({ autoOpen: false, width: 400, });
   $('#add_job_link').click(function(){ $('#add_dialog').dialog('open'); return false; });

   // Chart Overlay
   $('#chart_dialog').dialog({ 
      autoOpen: false, 
      width: $(window).width(), 
      buttons: { "Close": function() { $(this).dialog("close"); } } 
   });
   $('#chart_link').click(function(){ $('#chart_dialog').dialog('open'); return false; });

   //hover states on the static widgets
   $('#dialog_link, ul#icons li').hover(
      function() { $(this).addClass('ui-state-hover'); }, 
      function() { $(this).removeClass('ui-state-hover'); }
   );
});


</script>
</head>
<body onload="timer();">

<div id="container">
   <div id="header">
           <table width="100%">
           <tr>
           <td>
      <h1>
         DS Scheduler Web Console
      </h1>
           </td>
           <td>
            </td>
           </tr>
           </table>
   </div>
   <div id="navigation">
      <ul>
         <li><a href="#" id="add_job_link" class="ui-state-default ui-corner-all">Add Job</a></li>
         <!-- <li><a href="#" id="chart_link" class="ui-state-default ui-corner-all">View Chart</a></li> -->
         <li><a href="#" id="chart_link" class="ui-state-default ui-corner-all">View Graph</a></li>
         <li><div id="master_daemon_status"></div></li>
      </ul>
   </div>
   <div id="content">

<form id="select_jobs" name="select_jobs" onsubmit="return false;">
<?php echo viewJobs(); ?>

<input type="checkbox" onClick="toggle(this)" /> Select All ||
<i>With selected:</i>
<input type="button" onclick="return xajax_Action(xajax.getFormValues('select_jobs'), 'run_now');" value="Run Now" />
<input type="button" onclick="return xajax_Action(xajax.getFormValues('select_jobs'), 'kill');" value="Kill" />
<input type="button" onclick="return xajax_Action(xajax.getFormValues('select_jobs'), 'remove');" value="Delete" />
<input type="button" onclick="return xajax_Action(xajax.getFormValues('select_jobs'), 'disable');" value="Disable" />
<input type="button" onclick="return xajax_Action(xajax.getFormValues('select_jobs'), 'enable');" value="Enable" />
<input type="button" onclick="return xajax_Action(xajax.getFormValues('select_jobs'), 'reset');" value="Reset" />
</form>

<div id="chart_dialog" title="Last execution">
   <img src="blank.png" id="chart" alt="Graph">
   <script type="text/javascript">
      document.getElementById('chart').src = "gantt.php?w=" + $(window).width();
   </script>
</div>

<div id="add_dialog" title="Schedule New Job">
<form method="post" action="add.php" name="add_job">
   <table>
      <tr>
         <td>Name <input name="name" class="sminput"></td>
         <td>Host <input name="host" class="sminput"></td>
      </tr>
      <tr>
         <td>User <input name="user" class="sminput"></td>
         <td>Type <select name="type" class="sminput">
            <option value="cron">Cron Notation</option>
            <option value="dep">Child Job</option>
            <option value="file">File Trigger</option>
         </td>
      </tr>
      <tr>
         <td>Fails After <input name="end" class="sminput"></td>
         <td>Depends <select name="depends" class="sminput">
           <option value="0">--</option>
         <?php echo getJobspulldown(0); ?>
                     </select>
         </td>
         <td>Mode <select name="depmode" class="sminput">
           <option value="0">--</option>
         <?php echo getModepulldown(0); ?>
                     </select>
         </td>
      </tr>
      <tr>
         <td>Cron schedule <input name="cron" class="sminput"> </td>
         <td>Command <input name="cmd" class="sminput"> </td>
         <td>Log retention (in days) <input name="log_ret" class="sminput" value="30"> </td>
      </tr>
      <tr>
         <td colspan="2">Comment <textarea name="comment" ></textarea> </td>
      </tr>
      <tr>
         <td><button name="OK" type="submit">OK</button></td>
      </tr>
   </table>
</form>
</div>

<?php //TODO: echo editJob(); ?>

      </div>
      <div id="footer">
         <table width="100%">
         <tr><td align="left"><?php $usr = $_SERVER['PHP_AUTH_USER']; echo "Hello " . $usr; ?></td><td align="right">DS Scheduler Web Console 0.8</td></tr>
         </table>
      </div>
   </div>
</body>
</html>
