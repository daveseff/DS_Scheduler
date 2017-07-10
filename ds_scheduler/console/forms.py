from django import forms
from .models import Jobs, DepModes
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Field
from crispy_forms.bootstrap import FormActions

type_choices = [
  ('cron', 'Cron Notation'),
  ('dep', 'Child Job'),
  ('file', 'File Trigger'),
]

depmode_choices = [(dm.mode_id, dm.mode) for dm in DepModes.objects.all()]
all_jobs = [(job.id, job.name) for job in Jobs.objects.all()]
job_selection = [('0', 'N/A'),]
job_selection.extend(all_jobs)

class newJob(forms.ModelForm):
  id = forms.IntegerField(widget=forms.HiddenInput(), initial = '', required = False)
  name = forms.CharField(label='Name', max_length=255, required = True)
  host = forms.CharField(label='Host', max_length=30, required = True)
  user = forms.CharField(label='User', max_length=31, required = True)
  sched_type = forms.ChoiceField(label='Type', required = True)
  #fail_after = forms.CharField(label='Fails After (minutes)', max_length=255, required = True)
  depends = forms.ChoiceField(label='Depends', required = False)
  depmod_mode = forms.ChoiceField(label='Mode', initial = '0', required = False)
  reoccur = forms.CharField(label='Schedule', max_length=30, required = True)
  command = forms.CharField(label='Command', max_length=300, required = True)
  update_flag = forms.IntegerField(widget=forms.HiddenInput(), initial = 1, required = True)
  status = forms.IntegerField(widget=forms.HiddenInput(), initial = 99999, required = True)
  rc = forms.IntegerField(widget=forms.HiddenInput(), initial = 99999, required = True)
  event_trigger = forms.IntegerField(widget=forms.HiddenInput(), initial = 0, required = True)
  log_retention = forms.IntegerField(label='Log Retention (days)', initial = 30, required = True)
  comment = forms.CharField(label='Comment', max_length=255, widget = forms.TextInput(attrs={'class':'textbox'}), required = False)
  def __init__(self, *args, **kwargs):
    super(newJob, self).__init__(*args, **kwargs)
    self.helper = FormHelper()
    self.helper.form_id = 'add_job'
    self.helper.form_class = 'form-horizontal'
    self.helper.form_method = 'post'
    self.helper.form_action = '/'
    self.helper.layout = Layout(
      Field('id', type='hidden'),
      Field('name', css_class='form-control'),
      Field('host', css_class='form-control'),
      Field('user', css_class='form-control'),
      Field('sched_type', css_class='form-control'),
      #Field('fail_after', css_class='form-control'),
      Field('depends', css_class='form-control'),
      Field('depmod_mode', css_class='form-control'),
      Field('reoccur', css_class='form-control'),
      Field('command', css_class='form-control'),
      Field('log_retention', css_class='form-control'),
      Field('comment', css_class='form-control'),
      Field('update_flag', type='hidden'),
      Field('status', type='hidden'),
      Field('rc', type='hidden'),
      Field('event_trigger', type='hidden'),
      FormActions(
            Submit('save_changes', 'Save changes'),
      )
    )
    self.fields['depends'].choices = job_selection
    self.fields['depmod_mode'].choices = depmode_choices
    self.fields['sched_type'].choices = type_choices

  class Meta:
    model = Jobs
    fields = "__all__"
