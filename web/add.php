<?php
include "functions.php";
require_once 'dbconfig.php';

$db = new PDO("mysql:host={$dbserver};dbname={$database}", $username, $password);

$name = $_POST['name'];
$host = $_POST['host'];
$user = $_POST['user'];
$start_time = $_POST['start_time'];
$end = $_POST['end'];
$depends = $_POST['depends'];
$depmode = $_POST['depmode'];
$cron = $_POST['cron'];
$command = $_POST['cmd'];
$comment = $_POST['comment'];
$log_ret = $_POST['log_ret'];
$aof = $_POST['aof'];
$email = $_POST['email'];
$kof = $_POST['kof'];

global $db;
$query = "INSERT INTO jobs VALUES ( NULL , '${name}', '${host}', '${user}', '${start_time}' , '${end}' , '${depends}' , '${depmode}', 0, '${cron}', 99999 , 99999, '${command}', 1, '${comment}', '${log_ret}', '', '${aof}', '${email}', '${kof}');";
$db->exec($query);
Logit($query);
echo "<meta http-equiv='refresh' content='0;URL=index.php'>";
?>
