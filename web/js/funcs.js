function toggle(source) {
   checkboxes = document.getElementsByName('selected_job[]');
   for(var i in checkboxes)
      checkboxes[i].checked = source.checked;
}

