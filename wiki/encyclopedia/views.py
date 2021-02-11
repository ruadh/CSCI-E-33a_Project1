from django.shortcuts import render

from . import util

from markdown2 import Markdown

from django import forms

from django.urls import reverse

from django.http import HttpResponseRedirect

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
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            search = form.cleaned_data["search_for"]
            if search in util.list_entries():
                return HttpResponseRedirect(reverse("encyclopedia:entry", args = [search]))
            else: 
                return render(request, "encyclopedia/404.html", {"entry_title": search, "form": SearchForm()})

    # return render(request, "encyclopedia/dev.html", {"param": search})
    # if request.method == "POST":
    #     return HttpResponseRedirect(reverse("encyclopedia:dev"), {"param:"  "yo"}) # Redirect the user to the task list path, now that we have updated the list
    # else:
    #     return HttpResponseRedirect(reverse("encyclopedia:404"))

# Create a new entry


# FOR DEVELOPMENT ONLY:

def dev(request):
    return render(request, "encyclopedia/dev.html", {"param": request.method, "form": SearchForm()})
