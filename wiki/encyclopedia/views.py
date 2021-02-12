from django.shortcuts import render

from . import util

from markdown2 import Markdown

from django import forms

from django.urls import reverse

from django.http import HttpResponseRedirect

import random

# Search form class


class SearchForm(forms.Form):
    # Placeholder text via widget from: https://stackoverflow.com/questions/4101258/how-do-i-add-a-placeholder-on-a-charfield-in-django
    # search = forms.CharField(required=True, strip=True, widget=forms.TextInput(
    #     attrs={'placeholder': 'Search Encyclopedia'}))
    search_for = forms.CharField()


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(), "form": SearchForm()
    })

# Render a single wiki entry


def entry(request, entry):
    if entry in util.list_entries():
        # Convert the entry's markdown to HTML
        html = Markdown()
        txt = html.convert(util.get_entry(entry))
        return render(request, "encyclopedia/entry.html", {"entry_content": txt, "entry_title": entry, "form": SearchForm()})
    else:
        # If no entry exists, render the 404 error page
        return render(request, "encyclopedia/404.html", {"entry_title": entry, "form": SearchForm()})


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
                return HttpResponseRedirect(reverse("encyclopedia:entry", args = [search]))
            #If no exact match is found, find partial matches
            else: 
                # IN PROGRESS:  partial match
                indices = [i for i, s in enumerate(util.list_entries()) if search in s]     # Partial match logic from:  https://stackoverflow.com/questions/14849293/python-find-index-position-in-list-based-of-partial-string/14849322
                # return render(request, "encyclopedia/dev.html", {"param": indices, "form": SearchForm()}) 
                return render(request, "encyclopedia/search-results.html", {
        "entries": indices, "form": SearchForm()
        #TO DO:  return values instead of indices
    })


# Go to a random entry
def random_entry(request):
    # Select a pseudo-random entry from the list
    n = random.randrange(len(util.list_entries()))
    entr = util.list_entries()[n]
    # Pass that entry to the "entry" function to be rendered
    return entry(request, entr)


# Create a new entry


# FOR DEVELOPMENT ONLY:

def dev(request):
    return render(request, "encyclopedia/dev.html", {"param": util.list_entries(), "form": SearchForm()})
