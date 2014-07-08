<?php
include "functions.php";
$id = $_GET[id];

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

<script type="text/javascript">
         $(function(){

            // Accordion
            $("#accordion").accordion({ header: "h3" });
   
         });
      </script>

</head>
<body>
<a href="." id="back_to_main" class="ui-state-default ui-corner-all">Back to Jobs</a>
<br>
<table border="1px">
<div id="accordion">
<?php
foreach ($db->query("SELECT * FROM results WHERE id=${id} and LENGTH(output) > 1 ORDER BY end_date DESC") as $res)
{
   echo "<div>
   <h3><a href=\"#\">{$res[end_date]}</a></h3>
   <div>";
   echo nl2br($res[output]);
echo "</div>
</div>";
}
?>
</div>
<table>
</body>
</html>
