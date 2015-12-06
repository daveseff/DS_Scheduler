<?php
include "functions.php";
require_once 'dbconfig.php';

$db = new PDO("mysql:host={$dbserver};dbname={$database}", $username, $password);

$id = $_POST['id'];
$name = $_POST['name'];
$host = $_POST['host'];
$user = $_POST['user'];
$depends = $_POST['depends'];
$depmode = $_POST['depmode'];
$cron = $_POST['cron'];
$command = $_POST['cmd'];
$comment = $_POST['comment'];

$aof = (isset($_POST['aof'])?1:0);
$kof = (isset($_POST['kof'])?1:0);
$email = $_POST['email'];

global $db;
$query = "UPDATE  jobs SET name='{$name}', host='{$host}', user='{$user}', depends='{$depends}', depend_mode='{$depmode}', reoccur='{$cron}', command='{$command}', comment='{$comment}', aof='{$aof}', kof='{$kof}', email='{$email}', update_flag=1 where id='{$id}'";
$db->exec($query);
Logit($query);
echo "<meta http-equiv='refresh' content='0;URL=index.php'>";
?>
