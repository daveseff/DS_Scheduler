<?php 
   include "functions.php";
?>
<!DOCTYPE html>
<html>
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />
  <title>DS Scheduler Web Console</title>
  <link rel="stylesheet" type="text/css" href="css/layout.css" />
  <link rel="stylesheet" type="text/css" href="css/menu_style.css" />
  <link type="text/css" href="css/ui-lightness/jquery-ui-1.8.16.custom.css" rel="stylesheet" />
  <script type="text/javascript" src="js/jquery-1.6.2.min.js"></script>
  <script type="text/javascript" src="js/jquery-ui-1.8.16.custom.min.js"></script>
  <?php $xajax->printJavaScript();?>
<script type="text/javascript">
/* <![CDATA[ */
function timer()
{
   xajax_watchList();
   window.setInterval("xajax_watchList();",10000);//reload timer
}

function makesure()
{
   if (confirm('Are you sure you want to do this?'))
   {
      return true;
   }
   else
   {
      return false;
   }
}
/* ]]> */
</script>
<script type="text/javascript">
/* <![CDATA[ */
   $(function(){
      $('#dialog').dialog({
         autoOpen: false,
         width: 300,
         buttons: {
            "OK": function() { 
               $(this).dialog("close"); 
            }, 
            "Cancel": function() { 
               $(this).dialog("close"); 
            } 
         }
      });

      $('#dialog_link_2').click(function(){
         $('#dialog').dialog('open');
         return false;
      });
   )};
/* ]]> */
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
         <li><a href="" onclick="return xajax_show('addjob_form');">Add Job</a></li>
      </ul>
   </div>
   <div id="content-container">
        <div id="addjob_form" style="display:None;">
            <form method="post" action="add.php" name="add_job">
             <table>
             <tr>
               <td>Name <input name="name" class="sminput"></td>
               <td>Host <input name="host" class="sminput"></td>
               <td>User <input name="user" class="sminput"></td>
               <td>Start Time <input name="start" class="sminput"></td>
               <td>Fails After <input name="end" class="sminput"></td>
               <td>Depends <input name="depends" class="sminput"></td>
               <td>Cron schedule <input name="cron" class="sminput"> </td>
               <td>Command <input name="cmd" class="sminput"> </td>
               <td><button name="ADD">ADD</button></td>
             </tr>
             </table>
            </form>
          </div>
      <div id="content">

<?  echo viewJobs(); ?>
<!-- ui-dialog -->
<div id="dialog" title="Dialog Title">
<p>Commodo consequat.</p>
</div>

      </div>
      <div id="control">
         <div id="commands">
         </div>
      </div>
      <div id="footer">
         DS Scheduler Web Console 0.1
      </div>
   </div>
</div>

</body>
</html>
