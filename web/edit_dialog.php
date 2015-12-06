<?php
include "functions.php";
require_once 'dbconfig.php';

$db = new PDO("mysql:host={$dbserver};dbname={$database}", $username, $password);

$id = $_GET[id];

if($id)
{
   $job = $db->query("SELECT a.*, b.name as dep FROM jobs a LEFT OUTER JOIN jobs b ON a.depends = b.id where a.id = '{$id}'");
   $result = $job->fetch(PDO::FETCH_ASSOC);
}
else
  return;
?>
<form method="post" action="edit.php" name="add_job">
   <input type="hidden" name="id" value="<?php echo $id; ?>">
   <table>
      <tr>
         <td>Name <input name="name" class="sminput" value="<?php echo $result['name']; ?>"></td>
         <td>Host <input name="host" class="sminput" value="<?php echo $result['host']; ?>"></td>
         <td>User <input name="user" class="sminput" value="<?php echo $result['user']; ?>"></td>
      </tr>
      <tr>
         <td>Type <select name="type" class="sminput">
            <option value="cron">Cron Notation</option>
            <option value="dep">Child Job</option>
            <option value="file">File Trigger</option>
         </td>
      </tr>
      <tr>
         <!-- <td>Fails After <input name="end" class="sminput" value=""></td> -->
         <td>Depends <select name="depends" class="sminput" value="<?php echo $result['depends']; ?>">
                  <option value="0">--</option>
<?php echo getJobspulldown($result['dep']); ?>
                     </select>
         </td>
         <td>Mode <select name="depmode" class="sminput" value="<?php echo $result['mode']; ?>">
                  <option value="0">--</option>
<?php echo getModepulldown($result['depend_mode']); ?>
                  </select>
         </td>
      </tr>
      <tr>
         <td>Cron schedule <input name="cron" class="sminput" value="<?php echo $result['reoccur']; ?>"> </td>
         <td>Command <input name="cmd" class="sminput" value="<?php echo $result['command']; ?>"> </td>
         <td>Log Retention (in days) <input name="log_ret" class="sminput" value="<?php echo $result['log_retention']; ?>"> </td>
      </tr>
      <tr>
         <td colspan="2">Comment <textarea name="comment"><?php echo $result['comment']; ?></textarea> </td>
         <td colspan="2">Email on Failure<input type="checkbox" name="aof" <?php echo "checked",($result['aof'] == 1 ? '' : 'checked'); ?>></input></td>
         <td colspan="2">Email <input name="email" value="<?php echo $result['email']; ?>"></td>
      </tr>
      <tr>
         <td colspan="2">Kill on Failure<input type="checkbox" name="kof" <?php echo "checked",($result['kof'] == 1 ? '' : 'checked'); ?>></input></td>
         <td><button name="save" type="submit">Save</button></td>
      </tr>
   </table>
</form>
