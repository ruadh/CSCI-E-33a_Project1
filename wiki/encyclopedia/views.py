# Note:  This submission is based on homework I submitted when I took this class in Spring 2021
#        I have added comments marked "POST-GRADING" to show where I made changes based on Vlad's grading feedback
#        Other changes that were not based on TF feedback are not called out.

from django.shortcuts import render

from . import util

from markdown2 import Markdown

from django import forms

from django.urls import reverse

from django.http import HttpResponseRedirect

import random


# FORM CLASSES

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
        'entries': util.list_entries()})


# Render a single wiki entry
def entry(request, entry):
    # If the title exists, render it
    if entry.casefold() in [title.casefold() for title in util.list_entries()]:
        # Convert the entry's markdown to HTML
        # POST-GRADING:  Vlad advised me not to store Markdown() in a separate variable before converting
        txt = Markdown().convert(util.get_entry(entry))
        return render(
            request, 'encyclopedia/entry.html', {'entry_content': txt, 'entry_title': entry})
    else:
        # If no entry exists, render the 404 error page
        return render(request, 'encyclopedia/error-not-found.html', {'entry_title': entry})


# Search for an entry
# POST-GRADING:  Vlad pointed out that using a Django form for the search is klunky
# CITATION:  I inferred how to pass the query string from an HTML form from: https://stackoverflow.com/q/39842386
def search(request):
    # We only want to process GET requests from this form
    if request.method == 'GET':
        search = request.GET.get('q')
        entries = util.list_entries()
        # Convert the search string and entries list to caseless versions for comparison
        # POST-GRADING: I originally named these variables "_lower", which isn't 100% accurate
        search_caseless = search.casefold()
        entries_caseless = [title.casefold() for title in entries]
        # If an exact match exists, render its entry page using the entry's original case
        if search_caseless in entries_caseless:
            actual_title = entries[entries_caseless.index(search_caseless)]
            return HttpResponseRedirect(reverse('encyclopedia:entry', args=[actual_title]))
        # If no exact match is found, look for partial matches
        else:
            # POST-GRADING:  Using more compact syntax that Vlad provided in grading comments
            titles = [entry for entry in entries if search.casefold()
                      in entry.casefold()]
            # POST-GRADING:  Using conditional logic in the search-results template to handle no results found
            return render(request, 'encyclopedia/search-results.html', {'entries': titles, 'search': search})

# Render a random entry


def random_entry(request):
    # Select a pseudo-random entry from the list
    # POST-GRADING:  Vlad told me about random.choice in my grading comments
    entr = random.choice(util.list_entries())
    # POST-GRADING: Loading the entry in a new page, not rendering in the current one
    return HttpResponseRedirect(reverse('encyclopedia:entry', args=[entr]))


# Load a blank entry form
def create_entry(request):
    return render(request, 'encyclopedia/edit-entry.html', {'entry_form': EntryForm(), 'action': 'Create New'})


# Load an existing entry into the edit form
def load_entry(request, entry):
    # Validate the entry name before attempting to load
    if entry in util.list_entries():
        # CITATION:  initial values syntax from:  https://stackoverflow.com/a/936405
        form = EntryForm(
            initial={'title': entry, 'content': util.get_entry(entry), 'action': 'edit'})
        # CITATION:  Disabling the title field from:  https://stackoverflow.com/a/6862413
        form.fields['title'].widget = forms.HiddenInput()
        return render(
            request, 'encyclopedia/edit-entry.html',
            {'entry_form': form, 'action': 'edit', 'entry_title': entry})
    else:
        # If no entry exists, render the 404 error page
        return render(request, 'encyclopedia/error-not-found.html', {'entry_title': entry})


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
                return render(request, 'encyclopedia/duplicate-entry.html', {'entry_title': title})
            else:
                if form.cleaned_data['action'] == 'create':
                    # Create a new entry
                    # POST-GRADING: Not including the title in the editable body of the entry
                    util.save_entry(title, content)

                else:
                    # Save the edited entry
                    util.save_entry(title, content)
                return HttpResponseRedirect(reverse('encyclopedia:entry', args=[title]))
