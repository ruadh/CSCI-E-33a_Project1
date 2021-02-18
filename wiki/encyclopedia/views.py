from django.shortcuts import render

from . import util

from markdown2 import Markdown

from django import forms

from django.urls import reverse

from django.http import HttpResponseRedirect

import random


# FORM CLASSES

# Search form

class SearchForm(forms.Form):
    search = forms.CharField(
        required=True, strip=True, widget=forms.TextInput())


# Entry form for creating and editing entries

class EntryForm(forms.Form):
    title = forms.CharField(required=True, strip=True,
                            widget=forms.TextInput())
    content = forms.CharField(
        required=True, strip=True, widget=forms.Textarea())
    action = forms.CharField(initial='create', widget=forms.HiddenInput)


# FUNCTIONS

# Render the index page

def index(request):
    return render(request, 'encyclopedia/index.html', {
        'entries': util.list_entries(), 'search_form': SearchForm()
    })


# Render a single wiki entry

def entry(request, entry):
    # If the title exists, render it
    if entry.casefold() in [title.casefold() for title in util.list_entries()]:
        # Convert the entry's markdown to HTML
        html = Markdown()
        txt = html.convert(util.get_entry(entry))
        return render(
            request, 'encyclopedia/entry.html',
            {'entry_content': txt, 'entry_title': entry, 'search_form': SearchForm()})
    else:
        # If no entry exists, render the 404 error page
        return render(request, 'encyclopedia/error-not-found.html', {'entry_title': entry, 'search_form': SearchForm()})


# Search for an entry

def search(request):
    # We only want to process GET requests from this form
    if request.method == 'GET':
        form = SearchForm(request.GET)
        # Validate and clean the request and pull out the search string
        if form.is_valid():
            # Convert the search string and entries list to lowercase for comparison
            search = form.cleaned_data['search']
            entries = util.list_entries()
            search_lower = search.casefold()
            entries_lower = [title.casefold() for title in entries]
            # If an exact match exists, render its entry page
            if search_lower in entries_lower:
                # Render the page using the entry's original case
                actual_title = entries[entries_lower.index(search_lower)]
                return HttpResponseRedirect(reverse('encyclopedia:entry', args=[actual_title]))
            # If no exact match is found, look for partial matches
            else:
                # CITATION:  Enumeration approach based on:
                # https://stackoverflow.com/questions/14849293/python-find-index-position-in-list-based-of-partial-string/14849322
                indices = [i for i, s in enumerate(entries_lower) if search_lower in s]
                titles = [entries[i] for i in indices]
                if titles:
                    return render(request, 'encyclopedia/search-results.html',
                                  {'entries': titles, 'search_form': SearchForm()})
                # If no partial matches exist, send the user to the 404 error
                else:
                    return render(request, 'encyclopedia/error-not-found.html',
                                  {'entry_title': search, 'search_form': SearchForm()})


# Render a random entry

def random_entry(request):
    # Select a pseudo-random entry from the list
    n = random.randrange(len(util.list_entries()))
    entr = util.list_entries()[n]
    # Pass its title to the entry function to be rendered
    return entry(request, entr)


# Load a blank entry form

def create_entry(request):
    return render(
        request, 'encyclopedia/edit-entry.html',
        {'search_form': SearchForm(),
         'entry_form': EntryForm(),
         'action': 'Create New'})


# Load an existing entry into the edit form

def load_entry(request, entry):
    # Validate the entry name before attempting to load
    if entry in util.list_entries():
        # CITATION:  initial values syntax from:
        # https://stackoverflow.com/questions/936376/prepopulate-django-non-model-form
        form = EntryForm(initial={'title': entry, 'content': util.get_entry(entry), 'action': 'edit'})
        # Don't allow the user to change the title
        # CITATION:  modifying a field's widget from:
        # https://stackoverflow.com/questions/6862250/change-a-django-form-field-to-a-hidden-field
        form.fields['title'].widget = forms.HiddenInput()
        return render(
            request, 'encyclopedia/edit-entry.html',
            {'search_form': SearchForm(), 'entry_form': form, 'action': 'edit', 'entry_title': entry})
    else:
        # If no entry exists, render the 404 error page
        return render(request, 'encyclopedia/error-not-found.html', {'entry_title': entry, 'search_form': SearchForm()})


# Submit entry form (used to create or update existing)

def submit_entry(request):
    if request.method == 'POST':
        form = EntryForm(request.POST)
        # Validate and clean the request and pull out the form fields
        if form.is_valid():
            title = form.cleaned_data['title']
            content = form.cleaned_data['content']
            # Disallow creating a new entry with an existing title
            if (title.casefold() in [entry.casefold() for entry in util.list_entries()]
                    and form.cleaned_data['action'] == 'create'):
                return render(request, 'encyclopedia/duplicate-entry.html',
                              {'entry_title': title, 'search_form': SearchForm()})
            else:
                if form.cleaned_data['action'] == 'create':
                    # Create a new entry, adding the title formatted as h1
                    util.save_entry(title, '# ' + title + '\r\n' + content)
                else:
                    # Save the edited entry
                    util.save_entry(title, content)
                return HttpResponseRedirect(reverse('encyclopedia:entry', args=[title]))
