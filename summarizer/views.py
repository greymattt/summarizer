from django.shortcuts import render
from django.http import HttpResponse
from .forms import Linker
from .caption_util import main

# Create your views here.
def index(request):
    form = Linker()
    if request.method == "POST":
        form = Linker(request.POST)
        if form.is_valid():
            n = form.cleaned_data["link"]
            print("\n\n")
            print(n)
            print("\n\n")
            main(n)
    return render(request, "summarizer/index.html", {"form": form})
    # return HttpResponse("<h1>Test</h1>")
