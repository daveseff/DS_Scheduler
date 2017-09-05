from __future__ import unicode_literals
from django.shortcuts import render_to_response
from django.shortcuts import render
from django.core import serializers
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from .models import Jobs, Results
from .forms import newJob

def login(request):
  c = {}
  return render_to_response('console/login.html', c)

def auth_view(request):
  username = request.POST.get('username', '')
  password = request.POST.get('password', '')
  user = auth.authenticate(username=username, password=password)

  if user is not None:
    auth.login(request, user)
    return HttpResponseRedirect('/')
  else:
    return HttpResponseRedirect('/console/invalid')

def invalid_login(request):
  return render_to_response('console/invalid_login.html')

@login_required
def logout(request):
  auth.logout(request)
  return render_to_response('console/logout.html')

@login_required
def index(request):
  current_user = request.user
  data = {}

  if request.method == 'POST':
    if 'save_new_job' in request.POST:
      add_job = newJob(request.POST)
      if add_job.is_valid():
        add_job.save(commit=True)
      else:
        print add_job.errors
    # Job modifiers ( disable, delete, etc..)
    elif 'run_job_now' in request.POST:
      Jobs.objects.filter(id=request.POST['selected_job']).update(update_flag=1, event_trigger=1, rc=99999)
    elif 'kill_job' in request.POST:
      Jobs.objects.filter(id=request.POST['selected_job']).update(update_flag=4)
    elif 'delete_job' in request.POST:
      Jobs.objects.filter(id=request.POST['selected_job']).update(update_flag=2)
    elif 'disable_job' in request.POST:
      Jobs.objects.filter(id=request.POST['selected_job']).update(update_flag=3)
    elif 'enable_job' in request.POST:
      Jobs.objects.filter(id=request.POST['selected_job']).update(update_flag=1, status=99999)
    elif 'reset_job' in request.POST:
      Jobs.objects.filter(id=request.POST['selected_job']).update(update_flag=1, event_trigger=0, start_time=None, end_time=None, rc=99999, status=99999)

  add_job = newJob()

  data['current_user'] = current_user
  data['add_job'] = add_job
  data['jobs'] = Jobs.objects.all()
  return render(request, 'index.html', data)

@login_required
def log(request):
  job_id = request.GET['id']

  data = {}
  data['results'] = Results.objects.filter(id=job_id).order_by('end_date').exclude(output__isnull=True)

  return render(request, 'log.html', data)

@login_required
def render_status(request):
  data = serializers.serialize('json', Jobs.objects.all())
  return HttpResponse(data)

def startBatchJobs(request):
  print(request)
  return HttpResponse("{ok}", mimetype='application/json')
