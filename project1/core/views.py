from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.db.models import Q
from .models import StudyGroup, Subject, StudySession, StudyMaterial, GroupMembership, Profile, Comment
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import UserRegistrationForm

def home(request):
    subjects = Subject.objects.all()
    recent_groups = StudyGroup.objects.filter(is_active=True).order_by('-created_at')[:6]
    return render(request, 'core/home.html', {
        'subjects': subjects,
        'recent_groups': recent_groups
    })

class StudyGroupListView(ListView):
    model = StudyGroup
    template_name = 'core/group_list.html'
    context_object_name = 'groups'
    paginate_by = 12

    def get_queryset(self):
        queryset = StudyGroup.objects.filter(is_active=True)
        subject = self.request.GET.get('subject')
        if subject:
            queryset = queryset.filter(subject__id=subject)
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subjects'] = Subject.objects.all()
        return context

class StudyGroupDetailView(DetailView):
    model = StudyGroup
    template_name = 'core/group_detail.html'
    context_object_name = 'group'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['is_member'] = self.object.members.filter(id=self.request.user.id).exists()
            if context['is_member']:
                context['user_role'] = GroupMembership.objects.get(
                    user=self.request.user, 
                    group=self.object
                ).role
        context['upcoming_sessions'] = self.object.studysession_set.filter(
            status='scheduled'
        ).order_by('date', 'start_time')[:5]
        context['recent_materials'] = self.object.studymaterial_set.order_by('-created_at')[:5]
        context['comments'] = self.object.comments.filter(parent__isnull=True).select_related('author').prefetch_related('replies')
        return context

class StudyGroupCreateView(LoginRequiredMixin, CreateView):
    model = StudyGroup
    template_name = 'core/group_form.html'
    fields = ['name', 'description', 'subject', 'max_members']
    success_url = reverse_lazy('core:group_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        GroupMembership.objects.create(
            user=self.request.user,
            group=self.object,
            role='admin'
        )
        messages.success(self.request, 'Study group created successfully!')
        return response

@login_required
def join_group(request, pk):
    group = get_object_or_404(StudyGroup, pk=pk)
    if group.members.count() >= group.max_members:
        messages.error(request, 'This group is already full.')
        return redirect('core:group_detail', pk=pk)
    
    if not group.members.filter(id=request.user.id).exists():
        GroupMembership.objects.create(
            user=request.user,
            group=group,
            role='member'
        )
        messages.success(request, 'You have successfully joined the group!')
    return redirect('core:group_detail', pk=pk)

@login_required
def leave_group(request, pk):
    group = get_object_or_404(StudyGroup, pk=pk)
    membership = get_object_or_404(GroupMembership, user=request.user, group=group)
    if membership.role != 'admin' or group.groupmembership_set.filter(role='admin').count() > 1:
        membership.delete()
        messages.success(request, 'You have left the group.')
    else:
        messages.error(request, 'As the only admin, you cannot leave the group. Please assign another admin first.')
    return redirect('core:group_detail', pk=pk)

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to Study Groups!')
            return redirect('core:home')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def profile(request):
    user_groups = StudyGroup.objects.filter(members=request.user)
    administered_groups = StudyGroup.objects.filter(groupmembership__user=request.user, 
                                                  groupmembership__role='admin')
    upcoming_sessions = StudySession.objects.filter(
        group__in=user_groups,
        status='scheduled'
    ).order_by('date', 'start_time')[:5]
    
    return render(request, 'core/profile.html', {
        'user_groups': user_groups,
        'administered_groups': administered_groups,
        'upcoming_sessions': upcoming_sessions,
    })

class StudyGroupSearchView(ListView):
    model = StudyGroup
    template_name = 'core/search_results.html'
    context_object_name = 'groups'
    paginate_by = 12

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        subject = self.request.GET.get('subject', '')
        
        queryset = StudyGroup.objects.filter(is_active=True)
        
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(subject__name__icontains=query)
            )
        
        if subject:
            queryset = queryset.filter(subject_id=subject)
            
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subjects'] = Subject.objects.all()
        context['query'] = self.request.GET.get('q', '')
        context['current_subject'] = self.request.GET.get('subject', '')
        return context

# Comment views
@login_required
def add_comment(request, group_id):
    group = get_object_or_404(StudyGroup, pk=group_id)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Comment.objects.create(
                group=group,
                author=request.user,
                content=content
            )
            messages.success(request, 'Comment posted successfully!')
    return redirect('core:group_detail', pk=group_id)

@login_required
def add_reply(request, group_id, comment_id):
    group = get_object_or_404(StudyGroup, pk=group_id)
    parent_comment = get_object_or_404(Comment, pk=comment_id)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Comment.objects.create(
                group=group,
                author=request.user,
                content=content,
                parent=parent_comment
            )
            messages.success(request, 'Reply posted successfully!')
    return redirect('core:group_detail', pk=group_id)

@login_required
def edit_comment(request, group_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, author=request.user)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            comment.content = content
            comment.save()
            messages.success(request, 'Comment updated successfully!')
    return redirect('core:group_detail', pk=group_id)

@login_required
def delete_comment(request, group_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, author=request.user)
    if request.method == 'POST':
        comment.delete()
        messages.success(request, 'Comment deleted successfully!')
    return redirect('core:group_detail', pk=group_id)