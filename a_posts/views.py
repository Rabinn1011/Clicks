from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import *
from bs4 import BeautifulSoup
import requests
from django.contrib import messages
# Create your views here.


def home_view(request, tag=None):
    if tag:
        posts = Post.objects.filter(tags__slug =tag)
        tag = get_object_or_404(Tag, slug=tag)
    else:
        posts = Post.objects.all()
 
    categories = Tag.objects.all()    
    
    
    context = {
        'posts': posts,
        'categories' : categories,
        'tag' : tag
    }

    return render(request, 'a_posts/home.html', context )


def post_create_view(request):
    form = PostCreateForm()

    if request.method == 'POST':
        form = PostCreateForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)

            url = request.POST.get('url')  
            response = requests.get(url) 
            
            if response.status_code == 200:
                sourcecode = BeautifulSoup(response.text, 'html.parser')

                #  Extract image URL
                find_image = sourcecode.select('meta[content^="https://live.staticflickr.com/"]')
                if find_image:
                    post.image = find_image[0]['content']

                #  Extract title
                find_title = sourcecode.select('h1.photo-title')
                if find_title:
                    post.title = find_title[0].text.strip()

                #  Extract artist name
                find_artist = sourcecode.select('a.owner-name')
                if find_artist:
                    post.artist = find_artist[0].text.strip()

                post.save()
                form.save_m2m()
                return redirect('home')
            else:
                form.add_error('url', 'Failed to fetch data from Flickr.')

    return render(request, 'a_posts/post_create.html', {'form': form})


def post_delete_view(request,pk):
    
    
    post = get_object_or_404(Post, id=pk)
    
    if request.method == "POST":
        post.delete()
        messages.success(request,'Post Deleted Successfully!')
        return redirect('home')

    
    return render(request, 'a_posts/post_delete.html', {'post' : post})

def post_edit_view(request,pk):
    
    
    post = get_object_or_404(Post, id=pk)
    form = PostEditForm(instance=post)
    
    if request.method == "POST":
        form = PostEditForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request,'Post Updated Successfully!')
            return redirect('home')
    
    context = {
        'post' : post,
        'form' : form
    }
    
    return render(request, 'a_posts/post_edit.html', context)

def post_page_view(request,pk):
   
    post = get_object_or_404(Post, id=pk)
    
    return render(request, 'a_posts/post_page.html',{'post' : post})