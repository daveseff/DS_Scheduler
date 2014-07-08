<?php
require_once 'dbconfig.php';
include ( "jpgraph/src/jpgraph.php");
include ("jpgraph/src/jpgraph_gantt.php");

//$height=$_GET['h'];
$width=$_GET['w'];
$db = new PDO("mysql:host={$dbserver};dbname={$database}", $username, $password);

//$graph = new GanttGraph ($width - 50 ,$height - 50);
$graph = new GanttGraph ($width,0);
$graph->SetShadow();

// Add title and subtitle
$graph->title-> Set("Last Job Execution");
$graph->SetMarginColor('lightgreen@0.8');
$graph->SetBox(true,'yellow:0.6',2);
$graph->SetFrame(true,'darkgreen',4);
$graph->scale->divider->SetColor('yellow:0.6');
$graph->scale->dividerh->SetColor('yellow:0.6');
// Show day, week and month scale
//$graph->ShowHeaders( GANTT_HHOUR | GANTT_HDAY | GANTT_HWEEK | GANTT_HMONTH);
$graph->ShowHeaders( GANTT_HHOUR | GANTT_HDAY);
$graph->scale->hour->SetBackgroundColor( 'lightyellow:1.5' );
$graph->scale->hour->SetFont( FF_FONT1 );
$graph->scale->hour->SetStyle( HOURSTYLE_HMAMPM );
$graph->scale->hour->SetIntervall( '1:00' );


// Instead of week number show the date for the first day in the week
// on the week scale
$graph->scale->week->SetStyle(WEEKSTYLE_FIRSTDAY);

// Make the week scale font smaller than the default
$graph->scale->week->SetFont(FF_FONT0 );

// Use the short name of the month together with a 2 digit year
// on the month scale
$graph->scale->month->SetStyle( MONTHSTYLE_SHORTNAMEYEAR2);

$i = 0;
$jobs = 0;
foreach ($db->query("select distinct name from jobs") as $names)
{
   foreach ($db->query("select a.host, a.name, b.start_date, b.end_date, b.rc from jobs a, results b where b.start_date IS NOT NULL and b.end_date IS NOT NULL and a.id = b.id and a.name = '{$names['name']}' and DATE(b.end_date) = DATE(NOW()) order by a.host, a.name") as $jobs)
   {
      if (count($jobs) > 0)
      {
         $activity = new GanttBar ($i, $jobs['host']." : ". $jobs['name'], $jobs['start_date'], $jobs['end_date']);
         // Format the bar for the first activity

         // Yellow diagonal line pattern on a green background if success, red bg if fail
         if ($jobs['rc'] != 0)
         {
            $activity ->SetPattern(BAND_RDIAG, "yellow");
            $activity ->SetFillColor ("red"); 
         }
         else
         {
            $activity ->SetPattern(BAND_RDIAG, "blue");
            $activity ->SetFillColor ("green"); 
         }
         $graph->Add( $activity);
      }
   }
   if (count($jobs) > 0)
      $i++;
}
// Display the Gantt chart
$graph->Stroke();
?> 
