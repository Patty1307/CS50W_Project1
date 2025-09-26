from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
import markdown2

from . import util

class EntryForm(forms.Form):
    title = forms.CharField()
    text = forms.CharField(widget=forms.Textarea(attrs={
            "placeholder": "Write your text in markdown"}))

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def readentry(request, title):
    entries = util.list_entries()
    # Check if the entry exists and at the same time determine the correct spelling of the file name for the title.
    entry_title = next((e for e in entries if e.lower() == title.lower()), None)

    # When there is now entry, render error.html
    if entry_title is None:
        return render(request, "encyclopedia/error.html", {
            "errmsg": f"There is no entry called '{title}'.",
            "page_title": "Error"
        })

    # We already checked if there is any entry, but in case the file could not be retrieved render a diferent error
    content = util.get_entry(entry_title)
    if content is None:
        return render(request, "encyclopedia/error.html", {
            "errmsg": f"Oops, something went wrong. The file '{entry_title}' could not be found." 
        })

    # Convert markdown to html
    html_content = markdown2.markdown(content)

    # Render page
    return render(request, "encyclopedia/readentry.html", {
        "page_title": entry_title, 
        "entry": html_content
    })

def search(request):
    # Get the query
    query = request.GET.get("q", "")

    # Matching the entrys with the query
    entries = util.list_entries()
    results = [e for e in entries if query.lower() in e.lower()]

    # If there is only one match in the list an the query is an exact match, open directly the entry
    if len(results) == 1 and results[0].lower() == query.lower():
        return HttpResponseRedirect(reverse("readentry", kwargs={"title":results[0]}))

    # Else make a list of matches in the search template
    return render(request, "encyclopedia/search.html", {
        "entries": results,
        "query": query,
        "page_title": "Search"
    })

def createentry(request):
    Page_Title = "Create New Page"
    if request.method == "POST":
        # Get the Form data from the Post
        form = EntryForm(request.POST)
        # Check if the Data is valid. 
        if form.is_valid():
            # Extrakt the Data 
            Entry_title = form.cleaned_data["title"]
            # Format the text. Because of an unknown reason it creates line breakes
            text = form.cleaned_data["text"].replace('\r\n', '\n')
            
            # Check if any entry with this title exists.
            if util.get_entry(Entry_title):
                form.add_error("title", "A page with this title already exists")
                return render(request, "encyclopedia/entryworkshop.html", {
                "form": form,
                "title": Page_Title
                })
            
            # Save and redirect
            util.save_entry(Entry_title, text)
            return HttpResponseRedirect(reverse("readentry", kwargs={"title":Entry_title}))
        
    else:

        return render(request, "encyclopedia/entryworkshop.html",{
            "form": EntryForm(),
            "page_title": Page_Title,
            "form_action": reverse("createentry")
        })


def editentry(request, title):
    Page_Title = "Edit Page"
    entry_content = util.get_entry(title)
    
    if request.method == "POST":
        
        # Because we disabled the field title it can't be send in the Post, so we manual have to add it before we valid
        post = request.POST.copy()
        post["title"] = title
        form = EntryForm(post)
        
        #Validate
        if form.is_valid():
            # Format the text. Because of an unknown reason it creates line breakes
            new_text = form.cleaned_data["text"].replace('\r\n', '\n')
            util.save_entry(title, new_text)
            return HttpResponseRedirect(reverse("readentry", kwargs={"title": title}))

    else:

        form = EntryForm(initial={"title": title, "text": entry_content})
        form.fields["title"].disabled = True
        form.fields["title"].required = False

        return render(request, "encyclopedia/entryworkshop.html",{
            "form": form,
            "page_title": Page_Title,
            "form_action": reverse("editentry", kwargs={"title": title}),
            "entryname": title,
    })