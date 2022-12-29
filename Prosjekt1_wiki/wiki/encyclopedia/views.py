from django.shortcuts import render
from markdown2 import markdown
from django import forms
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.urls import reverse
import random

from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

# function for searching up entries and redrecting to entry if it exists else show related searches page


def search(request):
    if request.method == "GET":

        # storing get variables
        query = request.GET.get("q")

        # checking if the query exists in entries problem here with the query being
        if query in util.list_entries():

            # getting entry content with provided util function
            pagecontent = util.get_entry(query)

            # converting markdown entry to html
            searchcontent = markdown(pagecontent)

            # rendering page with passed variables of page content and title
            return render(request, "encyclopedia/entry.html", {
                "pagecontent": searchcontent, "title": query
            })

        # if the query does not exsist in the list of entries then a related entries page will be shown exampe of related search
        # if quered ytho then a list only containing python should be returned or if a entry is later added that contains ytho in the title should also be returned
        else:
            # storing all entries in a variable
            entries = util.list_entries()

            # empty list for storing entries with occurence of the related query
            filtered_entries = []

            # for loop iterating through all entries and appending entries related to query
            for entry in entries:
                if query in entry:
                    filtered_entries.append(entry)

            # rendering related search page with passed variable list of entries related to query
            return render(request, "encyclopedia/search.html", {
                "entries": filtered_entries
            })


# function for getting entries
def entry(request, title):

    # getting entry content with provided util function
    pagecontent = util.get_entry(title)

    # if pagecontent variable is empty then the entry does not exist and the notfound page is shown
    if not pagecontent:
        return render(request, "encyclopedia/NotFound", {
            "title": title
        })

    # converting markdown entry to html
    contentmarkeddown = markdown(pagecontent)

    # rendering page with passed variables of page content and title
    return render(request, "encyclopedia/entry.html", {
        "pagecontent": contentmarkeddown, "title": title
    })

# https://docs.djangoproject.com/en/4.0/ref/forms/widgets/
# https://docs.djangoproject.com/en/4.0/ref/forms/fields/#core-field-arguments
# links for later use
# class for forms in creating and editing functions


class newpageforms(forms.Form):
    # django auto rejects if fields are empty because it is assumed fields must be populated
    # title form
    title = forms.CharField(widget=forms.TextInput(
        attrs={'name': 'title', 'placeholder': 'Enter title'}), label='')

    #
    content = forms.CharField(widget=forms.Textarea(
        attrs={'name': 'pagecontent', 'placeholder': 'Please write entry in markdown format'}), label='')

# function for creating new wiki entry


def newpage(request):

    # checking if method called is post ie user has entered content into forms and hit submit
    if request.method == "POST":

        # getting entered form data
        formdata = newpageforms(request.POST)

        # checking if form is valid server side
        if formdata.is_valid():
            # unpacking form data
            title = formdata.cleaned_data['title']
            content = formdata.cleaned_data['content']

            # checking that title of entry does not already exists
            if title not in util.list_entries():

                # saving entry with provided util function from util.py
                util.save_entry(title, content)

                # redirecting to created entry page
                return HttpResponseRedirect(f"wiki/{title}")

            # checking if title on entered entry exists rerender page and show erro message
            elif title in util.list_entries():
                # https://docs.djangoproject.com/en/4.1/ref/contrib/messages/
                messages.error(
                    request, 'The title of the entry you are trying to create already exists! Either make the entry with another title or try searching for the entry and then edit the existing one')
                return render(request, "encyclopedia/newpage.html", {
                    "pagecontent": formdata
                })

    # default render create page
    else:
        return render(request, "encyclopedia/newpage.html", {
            "pagecontent": newpageforms()
        })


class editforms(forms.Form):
    # note for later maybe add feature to also edit title and overwrite old entry file
    content = forms.CharField(widget=forms.Textarea(
        attrs={'name': 'pagecontent', 'placeholder': 'Please write entry in markdown format'}), label='')


def edit(request, title):
    content = util.get_entry(title)

    editform = editforms(initial={'content': content})

    if request.method == "POST":

        editform = editforms(request.POST)

        if editform.is_valid():

            content = editform.cleaned_data['content']

            # saving entry with provided util function from util.py
            util.save_entry(title, content)

            # redirecting to created entry page
            return HttpResponseRedirect(f"/wiki/{title}")

    return render(request, "encyclopedia/edit.html", {
        "pagecontent": editform, "title": title
    })

# function for choosing random page


def randompage(request):

    # storing entries in variable listentries
    listentries = util.list_entries()

    # getting random entry from list https://www.w3schools.com/python/ref_random_choices.asp
    title = random.choice(listentries)

    # redirecting to created randomly chosen page
    return HttpResponseRedirect(f"/wiki/{title}")
