function toggle(source) {
   checkboxes = document.getElementsByName("selected_job[]");
   for(var i in checkboxes)
      checkboxes[i].checked = source.checked;
}

var $loading = $('.overlay').hide();

$(document)
  .ready(function () {
    setInterval(function() {
      $.get("render_status", function(data, status){
        var model = JSON.parse(data);
        for (var key in model) {
          var j = model[key].fields;
          var id = model[key].pk;
          $("#start_time_" + id).text(j.start_time);
          $("#end_time_" + id).text(j.end_time);
          if (j.depends > 0) { $("#depends_" + id).text(j.depends); }
          switch (j.depend_mode) {
            case 0: $("#dep_mode_" + id).text("ON_SUCCESS"); break;
            case 1: $("#dep_mode_" + id).text("ON_FAILURE"); break;
            case 2: $("#dep_mode_" + id).text("ON_KILL"); break;
          }
          $("#reoccur_" + id).text(j.reoccur);
          switch (j.rc){
            case 0:
              $("#result_" + id).text("SUCCESS");
              $("#result_" + id).css("backgroundColor", "#CFFFAB");
              break;
            case -9:
              $("#result_" + id).text("KILLED");
              $("#result_" + id).css("backgroundColor", "#FF7D7D");
              break;
            case 99999:
              $("#result_" + id).text("UNKNOWN");
              $("#result_" + id).css("backgroundColor", "#AEAEAE");
              break;
            case 99994:
              $("#result_" + id).text("OFFLINE");
              $("#result_" + id).css("backgroundColor", "#FF7D7D");
              break;
            default:
              $("#result_" + id).text("FAILED");
              $("#result_" + id).css("backgroundColor", "#FF7D7D");
              break;
          }
          switch (j.status) {
            case 0:
              $("#status_" + id).text("DONE");
              $("#status_" + id).css("backgroundColor", "#CFFFAB");
              break;
            case 99999:
              $("#status_" + id).text("PENDING");
              $("#status_" + id).css("backgroundColor", "#FFFFFF");
              break;
            case 99998:
              $("#status_" + id).text("RUNNING");
              $("#status_" + id).css("backgroundColor", "#ABD9FF");
              break;
            case 99997:
              $("#status_" + id).text("DISABLED");
              $("#status_" + id).css("backgroundColor", "#8D8D8D");
              break;
            case 99996:
              $("#status_" + id).text("KILLED");
              $("#status_" + id).css("backgroundColor", "#FF7D7D");
              break;
            case 99994:
              $("#status_" + id).text("OFFLINE");
              $("#status_" + id).css("backgroundColor", "#FF7D7D");
              break;
            default:
              $("#status_" + id).text("UNKNOWN");
              $("#status_" + id).css("backgroundColor", "#AEAEAE");
              break;
          }
          $("#pid_" + id).text(j.pid);
        }
      });
    }, 5000)
  })
  //.ajaxStart(function () { $loading.show(); })
  //.ajaxStop(function () { $loading.hide(); });

$("#btn_runNow").click(function(){ $.get("job_runnow", function(data, status){ }); });
