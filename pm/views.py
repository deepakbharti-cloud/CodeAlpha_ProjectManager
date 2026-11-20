from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
def register(request):
    form = UserCreationForm(request.POST or None)
    if form.is_valid():
        login(request, form.save()); return redirect('/')
    return render(request, 'registration/register.html', {'form': form})

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404
from .models import Project, Task, Comment, Notification

def _project(request, pk):
    p = get_object_or_404(Project, pk=pk)
    if p.owner != request.user and request.user not in p.members.all():
        raise Http404
    return p

def _notify(users, msg, link, exclude):
    for u in set(users):
        if u and u != exclude: Notification.objects.create(user=u, message=msg, link=link)

@login_required
def dashboard(request):
    if request.method == 'POST' and request.POST.get('name', '').strip():
        p = Project.objects.create(name=request.POST['name'].strip(), description=request.POST.get('description', ''), owner=request.user)
        p.members.add(request.user); return redirect('board', pk=p.pk)
    ps = Project.objects.filter(Q(owner=request.user) | Q(members=request.user)).distinct()
    return render(request, 'pm/dashboard.html', {'projects': ps})

@login_required
def board(request, pk):
    p = _project(request, pk)
    cols = [(k, label, p.tasks.filter(status=k).select_related('assignee')) for k, label in Task.STATUS]
    return render(request, 'pm/board.html', {'p': p, 'cols': cols, 'members': p.members.all()})

@login_required
def add_member(request, pk):
    p = _project(request, pk)
    if request.method == 'POST':
        u = User.objects.filter(username=request.POST.get('username', '').strip()).first()
        if u:
            p.members.add(u); _notify([u], f'You were added to project "{p.name}"', f'/project/{p.pk}/', request.user)
            messages.success(request, f'{u.username} added')
        else: messages.error(request, 'User not found')
    return redirect('board', pk=pk)

@login_required
def add_task(request, pk):
    p = _project(request, pk)
    if request.method == 'POST' and request.POST.get('title', '').strip():
        a = p.members.filter(pk=request.POST.get('assignee') or 0).first()
        t = Task.objects.create(project=p, title=request.POST['title'].strip(), description=request.POST.get('description', ''),
                                assignee=a, due=request.POST.get('due') or None)
        _notify([a], f'New task assigned: {t.title}', f'/task/{t.pk}/', request.user)
    return redirect('board', pk=pk)

@login_required
def task(request, pk):
    t = get_object_or_404(Task, pk=pk); p = _project(request, t.project_id)
    if request.method == 'POST':
        if 'text' in request.POST and request.POST['text'].strip():
            Comment.objects.create(task=t, author=request.user, text=request.POST['text'].strip())
            _notify([t.assignee, p.owner], f'{request.user.username} commented on "{t.title}"', f'/task/{t.pk}/', request.user)
        elif 'status' in request.POST and request.POST['status'] in dict(Task.STATUS):
            t.status = request.POST['status']; t.save()
        elif 'assignee' in request.POST:
            t.assignee = p.members.filter(pk=request.POST['assignee'] or 0).first(); t.save()
            _notify([t.assignee], f'Task assigned to you: {t.title}', f'/task/{t.pk}/', request.user)
        return redirect('task', pk=pk)
    return render(request, 'pm/task.html', {'t': t, 'p': p, 'members': p.members.all(), 'statuses': Task.STATUS})

@login_required
def notifications(request):
    items = list(request.user.notifications.all()[:50])
    request.user.notifications.filter(read=False).update(read=True)
    return render(request, 'pm/notifications.html', {'items': items})
