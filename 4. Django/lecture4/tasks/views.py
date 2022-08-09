from django.http import HttpResponseRedirect
from django import forms
from django.shortcuts import render
from django.urls import reverse

class NewTaskForm(forms.Form):
    task = forms.CharField(label="New Task")
    priority = forms.IntegerField(label="Priority", min_value=1, max_value=10)

# Create your views here.
def index(request):
    if 'tasks' not in request.session:
        request.session['tasks'] = []

    return render(request, 'tasks/index.html', {
        'tasks': request.session['tasks']
    })

def add(request):
    if request.method == 'POST':
        form = NewTaskForm(request.POST)
        if form.is_valid():
            # get the data from the form (tasks) and store it to into the array
            task = form.cleaned_data['task']
            request.session['tasks'] += [task]
            return HttpResponseRedirect(reverse('tasks:index'))
        else:
            # renders the same page with an error field, indicating a cause
            return render(request, 'tasks/add.html', {
                'form': form
            })

    return render(request, 'tasks/add.html', {
        'form': NewTaskForm()
    })
