import csv
import datetime
from typing import List
from django.shortcuts import render, redirect
from service.models import Post, Comment
from django.views.generic import ListView, DeleteView, CreateView, UpdateView, DetailView
from .forms import PostForm, CommentForm, UserRegisterForm
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse


def index(req):
    return render(req, 'index.html')

@login_required
def about(req):
    return render(req, 'about.html')

class RegisterForm(SuccessMessageMixin, CreateView):
    form_class = UserRegisterForm
    success_message = "%(username)s was created successfully" 
    template_name = 'register.html'
    success_url = reverse_lazy('login')

class PostView(ListView):
    model = Post
    template_name = 'index.html'
    ordering = ['-created_at']

class DeatailPostView(LoginRequiredMixin, DetailView):
    login_url = 'login'
    model = Post
    template_name = 'detail_post.html'

# class CreatePostView(LoginRequiredMixin, CreateView, SuccessMessageMixin):
#     form_class = PostForm
#     success_message = "Post %(title)s was created successfully"
#     model = Post
#     template_name = 'create_post.html'
#     success_url = reverse_lazy('index')
#     login_url = 'login'

def create_post(req):
    form = PostForm()
    if req.method == "POST":
        form = PostForm(req.POST)
        if form.is_valid():
            new_post = form.save()
            new_post.name = req.user.username
            new_post.save()
            title = form.cleaned_data.get("title")
            messages.success(req, f"Post {title} was created successfully")
            return redirect('index')
    return render(req, "create_post.html", {"form":form})


class UpdatePostView(PermissionRequiredMixin, UpdateView):
    permission_required = 'service.change_post'
    login_url = 'login'
    model = Post
    template_name = 'create_post.html'
    form_class = PostForm

class DeletePostView(PermissionRequiredMixin, DeleteView):
    permission_required = 'service.delete_post'
    login_url = 'login'
    model = Post
    template_name = 'delete_post.html'
    success_url = reverse_lazy('index')

class AddCommentView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    login_url = 'login'
    model = Comment
    template_name = 'add_comment.html'
    form_class = CommentForm
    success_message = "Comment was created successfully" 

    def form_valid(self, form):
        form.instance.post_id = self.kwargs['pk']
        return super().form_valid(form)
        

def upload(req):
    context = {}
    if req.method == "POST":
        uploaded_file = req.FILES['file']
        file = FileSystemStorage()
        name = file.save(uploaded_file.name, uploaded_file)
        context['url'] = file.url(name)
    return render(req, "upload.html", context)


def download(req):
    response = HttpResponse(content_type = 'text/csv')
    writer = csv.writer(response)
    writer.writerow(['title', 'description', 'created_at'])

    for row in Post.objects.all().values_list('title', 'description', 'created_at'):
        writer.writerow(row)
    filename = str(datetime.datetime.now()) + 'posts.csv'
    response["Content-Disposition"] = f"attachment; filename = {filename}"

    return response