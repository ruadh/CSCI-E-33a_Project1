from django.shortcuts import render

from . import util

from markdown2 import Markdown

from django import forms

from django.urls import reverse

from django.http import HttpResponseRedirect

import random


# FORM CLASSES
# CITATION:  Placeholder text via widget from https://stackoverflow.com/questions/4101258/how-do-i-add-a-placeholder-on-a-charfield-in-django

# Search form object
class SearchForm(forms.Form):
    search_for = forms.CharField(required=True, strip=True, widget=forms.TextInput(
        attrs={'placeholder': 'Search Encyclopedia'}))

# Entry form object  (used for both creating and editing entries)
class EntryForm(forms.Form):
    title = forms.CharField(required=True, strip=True, widget=forms.TextInput(
        attrs={'placeholder': 'Title'}))
    content = forms.CharField(required=True, strip=True, widget=forms.Textarea(
        attrs={'placeholder': 'Body'}))
    action = forms.CharField(initial="create", widget=forms.HiddenInput)


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(), "search_form": SearchForm()
    })


# FUNCTIONS

# Render a single wiki entry

def entry(request, entry):
    if entry in util.list_entries():
        # Convert the entry's markdown to HTML
        html = Markdown()
        txt = html.convert(util.get_entry(entry))
        return render(request, "encyclopedia/entry.html", {"entry_content": txt, "entry_title": entry, "search_form": SearchForm()})
    else:
        # If no entry exists, render the 404 error page
        return render(request, "encyclopedia/error-not-found.html", {"entry_title": entry, "search_form": SearchForm()})


# Search for an entry

def search(request):
    # We only want to process GET requests from this form
    if request.method == "GET":
        form = SearchForm(request.GET)
        # Validate and clean the request and pull out the search string
        if form.is_valid():
            search = form.cleaned_data["search_for"]
            # If the search string matches an entry, render it using the "entry" function
            if search in util.list_entries():
                return HttpResponseRedirect(reverse("encyclopedia:entry", args=[search]))
            # If no exact match is found, find partial matches
            else:
                # CITATION:  Enumeration approach based on https://stackoverflow.com/questions/14849293/python-find-index-position-in-list-based-of-partial-string/14849322
                indices = [i for i, s in enumerate(
                    util.list_entries()) if search in s]
                # CITATION:  list comprehension approach based on https://stackoverflow.com/questions/25082410/apply-function-to-each-element-of-a-list  (I new this from a previous course, but I forgot)
                titles = [ util.list_entries()[i] for i in indices]
                return render(request, "encyclopedia/search-results.html", {
                    "entries": titles, "search_form": SearchForm()
                }
                )


# Go to a random entry

def random_entry(request):
    # Select a pseudo-random entry from the list
    n = random.randrange(len(util.list_entries()))
    entr = util.list_entries()[n]
    # Pass that entry to the "entry" function to be rendered
    return entry(request, entr)


# Create a new entry

def create_entry(request):
    return render(request, "encyclopedia/edit-entry.html", {
            "search_form": SearchForm(), "entry_form": EntryForm(), "action": "Create New"
        })


# Load an existing entry to be edited

def load_entry(request, entry):
    # Validate the entry name before attempting to load
    if entry in util.list_entries():
        # CITATION:  initial syntax from:  https://stackoverflow.com/questions/936376/prepopulate-django-non-model-form
        form = EntryForm(initial={"title": entry, "content": util.get_entry(entry), "action": "edit" } )
        return render(request, "encyclopedia/edit-entry.html", {"search_form": SearchForm(), "entry_form": form, "action": "Edit" } )
    else:
        # If no entry exists, render the 404 error page
        return render(request, "encyclopedia/error-not-found.html", {"entry_title": entry, "search_form": SearchForm()})


# Submit entry form (create or update existing)

def submit_entry(request):
    if request.method == "POST":
        form = EntryForm(request.POST)
        # Validate and clean the request and pull out the form fields
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            # If we are trying to create a new entry, but one already exists with this title, show an error message
            if title in util.list_entries() and form.cleaned_data["action"] == "create":
                return render(request, "encyclopedia/duplicate-entry.html", {"entry_title": title, "search_form": SearchForm()})
            else:
                if form.cleaned_data["action"] == "create":
                    # Create a new entry, adding the title, formatted as h1
                    util.save_entry(title, "# " + title + "\r\n" + content)
                else:
                    # Save the edited entry (not adding the title, since it should already be there)
                    util.save_entry(title, content)
                return HttpResponseRedirect(reverse("encyclopedia:entry", args=[title]))

# FOR DEVELOPMENT ONLY:

def dev(request, param):
    return render(request, "encyclopedia/dev.html", {"param": param, "search_form": SearchForm()})
