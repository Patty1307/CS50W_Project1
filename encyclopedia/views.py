from django.shortcuts import render
import markdown2

from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def readentry(request, title):
    entries = util.list_entries()
    # Check if the entry exists and at the same time determine the correct spelling of the file name for the title.
    entry = next((e for e in entries if e.lower() == title.lower()), None)

    # When there is now entry, render error.html
    if entry is None:
        return render(request, "encyclopedia/error.html", {
            "errmsg": f"There is no entry called '{title}'."
        })

    # We already checked if there is any entry, but in case the file could not be retrieved render a diferent error
    content = util.get_entry(entry)
    if content is None:
        return render(request, "encyclopedia/error.html", {
            "errmsg": f"Oops, something went wrong. The file '{entry}' could not be found." 
        })

    # Convert markdown to html
    html_content = markdown2.markdown(content)

    # Render page
    return render(request, "encyclopedia/readentry.html", {
        "title": entry, 
        "entry": html_content
    })

def search(request):
    query = request.GET.get("q", "")

    # Matching the entrys with der query
    entries = util.list_entries()
    results = [e for e in entries if query.lower() in e.lower()]

    return render(request, "encyclopedia/search.html", {
        "entries": results,
        "query": query
    })