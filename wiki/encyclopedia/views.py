from django.shortcuts import render

from . import util

from markdown2 import Markdown

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

# Render a single wiki entry
def entry(request, entry):
    html = Markdown()
    txt = html.convert(util.get_entry(entry))
    return render(request, "encyclopedia/entry.html", { "entry_content": txt, "entry_title": entry } )

# Render the search results page
def search_results(request):
    return render(request, "encyclopedia/search-results.html", {
        "entries": util.list_entries()
    })