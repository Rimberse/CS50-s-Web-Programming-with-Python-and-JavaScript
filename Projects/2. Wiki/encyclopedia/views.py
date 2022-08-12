from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django import forms
from django.shortcuts import redirect
from django.core.exceptions import ValidationError
from markdown2 import Markdown
import logging
import random
from . import util

markdowner = Markdown()

class newPageForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={'name': 'title'}))
    content = forms.CharField(widget=forms.Textarea(attrs={'name': 'content', 'style': 'width: 85%; height: 15em;'}))

class editPageForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea(attrs={'name': 'content', 'style': 'width: 95%; height: 15em;'}))

# Main entry page
def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

# Individual wiki entries
def page(request, entry):
    return render(request, 'encyclopedia/page.html', {
        'entry': entry.capitalize(),
        'content': markdowner.convert(util.get_entry(entry)) if util.get_entry(entry) else None
    })

# Performs a query for a given entry
def search(request):
    # Get POST parameter, used to filter the wiki entries
    filter_by = request.POST.get('query', None).lower()
    logging.debug(f'Search for: {filter_by}')
    logging.info(f'Found matches: {[entry for entry in util.list_entries() if filter_by in entry.lower()]}')

    # Check if the query matches one of the entries, if it the case, then redirect the user to entry's page
    if filter_by in [entry.lower() for entry in util.list_entries()]:
        return redirect('page', entry=filter_by.capitalize())

    # Finally, render the page with the entries corresponding to user's query
    return render(request, 'encyclopedia/index.html', {
        'entries': [entry for entry in util.list_entries() if filter_by.strip() in entry.lower()]
    })

# Permits the user to add a new entry to wiki
def add(request):
    if request.method == 'POST':
        logging.debug(request.POST)
        form = newPageForm(request.POST)

        if form.is_valid():
            title = form.cleaned_data['title']
            content = form.cleaned_data['content']

            if not util.get_entry(title):
                util.save_entry(title, content)
                # passing parameters to reverse function, which are expected on 'page' endpoint call
                return HttpResponseRedirect(reverse('page', kwargs={'entry': title}))
            else:
                raise ValidationError((f'Error: {title} entry already exists'))
        else:
            return render(request, 'encyclopedia/new_page.html', {
                'form': form
            })

    return render(request, 'encyclopedia/new_page.html', {
        'form': newPageForm()
    })

# Permits the user to edit entry's content
def modify(request, entry):
    if request.method == 'POST':
        logging.debug(request.POST)
        form = editPageForm(request.POST)

        if form.is_valid():
            content = form.cleaned_data['content']

            util.save_entry(entry, content)
            return HttpResponseRedirect(reverse('page', kwargs={'entry': entry}))
        else:
            return render(request, 'encyclopedia/edit_page.html', {
                'form': form
            })

    return render(request, 'encyclopedia/edit_page.html', {
        'entry': entry,
        'form': editPageForm(initial={'content': util.get_entry(entry)})
    })

# Permits the user to see the random page
def randomize(request):
    # Generate random number between the leftmost and righmost indices of an array
    random_number = random.randint(0, len(util.list_entries()) - 1)
    # Retrieve it's entry name
    entry = util.list_entries()[random_number]
    logging.debug(f'Randomized: {entry} entry')

    return render(request, 'encyclopedia/page.html', {
        'entry': entry,
        'content': markdowner.convert(util.get_entry(entry))
    })
