from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, authenticate
from django.db.models import Q, Count
from django.contrib.auth.models import User
from django.utils import timezone
import datetime
import json
import csv
from .models import StudyGroup, Subject, StudySession, StudyMaterial, GroupMembership, Profile, Comment
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from .forms import UserRegistrationForm, StudyGroupForm, StudySessionForm, StudyMaterialForm, ProfileEditForm
from django.http import HttpResponse

def home(request):
    subjects = Subject.objects.all()
    recent_groups = StudyGroup.objects.filter(is_active=True).order_by('-created_at')[:6]
    return render(request, 'core/home.html', {
        'subjects': subjects,
        'recent_groups': recent_groups
    })

def login_view(request):
    from django.contrib.auth.forms import AuthenticationForm
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('core:home')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def get_started_view(request):
    # Simple landing page, could redirect to register or show info
    return render(request, 'core/get_started.html')

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
        context['is_member'] = False
        context['user_role'] = None
        
        if self.request.user.is_authenticated:
            context['is_member'] = self.object.members.filter(id=self.request.user.id).exists()
            if context['is_member']:
                membership = GroupMembership.objects.get(
                    user=self.request.user, 
                    group=self.object
                )
                context['user_role'] = membership.role
        
        context['upcoming_sessions'] = self.object.studysession_set.filter(
            status='scheduled'
        ).order_by('date', 'start_time')[:5]
        context['recent_materials'] = self.object.studymaterial_set.order_by('-created_at')[:5]
        context['comments'] = self.object.comments.filter(parent__isnull=True).select_related('author').prefetch_related('replies')

        # Group-level stats
        import datetime, json

        # Date filter window from query params (defaults to last 12 weeks)
        today = timezone.localdate()
        default_end = today
        default_start = default_end - datetime.timedelta(weeks=12)

        q_from = self.request.GET.get('from')
        q_to = self.request.GET.get('to')
        start_date = default_start
        end_date = default_end
        def parse_date(s):
            try:
                return datetime.date.fromisoformat(s)
            except Exception:
                return None
        preset = self.request.GET.get('preset')
        presets_weeks = {'4w': 4, '8w': 8, '12w': 12, '26w': 26}
        if preset in presets_weeks:
            end_date = default_end
            start_date = end_date - datetime.timedelta(weeks=presets_weeks[preset])
            context['group_filter_preset'] = preset
        else:
            if q_from:
                pd = parse_date(q_from)
                if pd:
                    start_date = pd
            if q_to:
                pd = parse_date(q_to)
                if pd:
                    end_date = pd
        if start_date > end_date:
            start_date, end_date = end_date, start_date

        # Cap range to a maximum of ~26 weeks for charting
        max_weeks = 26
        total_days = (end_date - start_date).days
        if total_days > max_weeks * 7:
            start_date = end_date - datetime.timedelta(weeks=max_weeks)

        context['group_filter_start'] = start_date.isoformat()
        context['group_filter_end'] = end_date.isoformat()

        sessions_qs = self.object.studysession_set.filter(date__gte=start_date, date__lte=end_date).only('date', 'start_time', 'end_time', 'created_by')
        # Totals
        total_seconds = 0
        for s in sessions_qs:
            if s.start_time and s.end_time:
                start_dt = datetime.datetime.combine(s.date, s.start_time)
                end_dt = datetime.datetime.combine(s.date, s.end_time)
                delta = end_dt - start_dt
                if delta.total_seconds() > 0:
                    total_seconds += delta.total_seconds()
        group_total_hours = round(total_seconds / 3600, 2)
        context['group_total_hours'] = group_total_hours
        context['group_total_sessions'] = sessions_qs.count()
        context['group_total_materials'] = self.object.studymaterial_set.count()
        context['group_total_comments'] = self.object.comments.count()

        # Weekly buckets (last 12 weeks for this group)
        # Determine aligned week buckets from start_date..end_date
        # Align to Mondays
        start_week = start_date - datetime.timedelta(days=start_date.weekday())
        end_week = end_date - datetime.timedelta(days=end_date.weekday())
        week_starts = []
        ws = start_week
        while ws <= end_week:
            week_starts.append(ws)
            ws = ws + datetime.timedelta(weeks=1)
        # Ensure at least one bucket exists
        if not week_starts:
            week_starts = [start_week]
        week_labels = [ws.strftime('%d %b') for ws in week_starts]
        sessions_per_week = [0] * len(week_starts)
        hours_per_week = [0.0] * len(week_starts)

        start_range = week_starts[0]
        end_range = week_starts[-1] + datetime.timedelta(days=7)
        bucket_qs = sessions_qs.filter(date__gte=start_range, date__lt=end_range).only('date','start_time','end_time')
        # Map week_start to index for O(1) lookup
        week_index = {ws: idx for idx, ws in enumerate(week_starts)}
        for s in bucket_qs:
            s_week_start = s.date - datetime.timedelta(days=s.date.weekday())
            idx = week_index.get(s_week_start)
            if idx is None:
                continue
            sessions_per_week[idx] += 1
            if s.start_time and s.end_time:
                start_dt = datetime.datetime.combine(s.date, s.start_time)
                end_dt = datetime.datetime.combine(s.date, s.end_time)
                delta = end_dt - start_dt
                if delta.total_seconds() > 0:
                    hours_per_week[idx] += round(delta.total_seconds() / 3600, 2)

        context['group_charts_json'] = json.dumps({
            'week_labels': week_labels,
            'sessions_per_week': sessions_per_week,
            'hours_per_week': [round(h, 2) for h in hours_per_week],
                # scatter and histogram for group range
                'scatter_points': [
                    {
                        'x': round(s.start_time.hour + (s.start_time.minute / 60.0), 2),
                        'y': round((datetime.datetime.combine(s.date, s.end_time) - datetime.datetime.combine(s.date, s.start_time)).total_seconds() / 3600.0, 2)
                    }
                    for s in sessions_qs
                    if s.start_time and s.end_time and (datetime.datetime.combine(s.date, s.end_time) - datetime.datetime.combine(s.date, s.start_time)).total_seconds() > 0
                ],
                'hist_labels': ['0-0.5h', '0.5-1h', '1-1.5h', '1.5-2h', '2-3h', '3-4h', '4-6h', '6h+'],
                'hist_counts': (lambda _bins: (
                    (lambda counts: [counts[i] for i in range(len(counts))])(
                        (lambda counts: (
                            [
                                (
                                    (counts.__setitem__(i, counts[i] + 1)) or counts[i]
                                ) if (_bins[i] <= (
                                    (datetime.datetime.combine(s.date, s.end_time) - datetime.datetime.combine(s.date, s.start_time)).total_seconds() / 3600.0
                                ) < _bins[i+1]) else counts[i]
                                for s in sessions_qs
                                for i in range(len(_bins)-1)
                                if s.start_time and s.end_time and (datetime.datetime.combine(s.date, s.end_time) - datetime.datetime.combine(s.date, s.start_time)).total_seconds() > 0
                            ] and counts
                        ))([0]*(len(_bins)-1))
                    )
                ))([0, 0.5, 1, 1.5, 2, 3, 4, 6, 1e9])
        })

        # Top 5 members by sessions and hours in range
        # Sessions per creator
        creator_counts = (sessions_qs
                          .values('created_by__username')
                          .annotate(count=Count('id'))
                          .order_by('-count'))
        # Hours per creator (computed in Python due to separate time fields)
        hours_by_user = {}
        for s in sessions_qs:
            if s.start_time and s.end_time:
                start_dt = datetime.datetime.combine(s.date, s.start_time)
                end_dt = datetime.datetime.combine(s.date, s.end_time)
                secs = max((end_dt - start_dt).total_seconds(), 0)
                key = getattr(s.created_by, 'username', 'Unknown')
                hours_by_user[key] = hours_by_user.get(key, 0.0) + secs / 3600.0

        # Merge counts and hours
        merged = {}
        for row in creator_counts:
            user = row['created_by__username'] or 'Unknown'
            merged[user] = {'user': user, 'sessions': row['count'], 'hours': 0.0}
        for user, hrs in hours_by_user.items():
            merged.setdefault(user, {'user': user, 'sessions': 0, 'hours': 0.0})
            merged[user]['hours'] = round(hrs, 2)

        top_members = sorted(merged.values(), key=lambda x: (-x['hours'], -x['sessions'], x['user']))[:5]
        context['group_top_members'] = top_members
        return context

@login_required
def group_stats_export(request, group_id):
    """Export group sessions for the selected date range as CSV."""
    group = get_object_or_404(StudyGroup, pk=group_id)
    # Only members can export
    if not group.members.filter(id=request.user.id).exists():
        return HttpResponse('Forbidden', status=403)

    today = timezone.localdate()
    default_end = today
    default_start = default_end - datetime.timedelta(weeks=12)

    q_from = request.GET.get('from')
    q_to = request.GET.get('to')
    preset = request.GET.get('preset')

    start_date = default_start
    end_date = default_end

    def parse_date(s):
        try:
            return datetime.date.fromisoformat(s)
        except Exception:
            return None

    presets_weeks = {'4w': 4, '8w': 8, '12w': 12, '26w': 26}
    if preset in presets_weeks:
        end_date = default_end
        start_date = end_date - datetime.timedelta(weeks=presets_weeks[preset])
    else:
        if q_from:
            pd = parse_date(q_from)
            if pd:
                start_date = pd
        if q_to:
            pd = parse_date(q_to)
            if pd:
                end_date = pd
        if start_date > end_date:
            start_date, end_date = end_date, start_date

    sessions_qs = group.studysession_set.filter(date__gte=start_date, date__lte=end_date).order_by('date', 'start_time')

    response = HttpResponse(content_type='text/csv')
    filename = f"group_{group_id}_sessions_{start_date.isoformat()}_to_{end_date.isoformat()}.csv"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)
    writer.writerow(['date', 'start_time', 'end_time', 'duration_hours', 'title', 'created_by', 'is_online', 'location', 'meeting_link', 'status'])

    for s in sessions_qs:
        duration_hours = ''
        if s.start_time and s.end_time:
            start_dt = datetime.datetime.combine(s.date, s.start_time)
            end_dt = datetime.datetime.combine(s.date, s.end_time)
            secs = max((end_dt - start_dt).total_seconds(), 0)
            duration_hours = round(secs / 3600.0, 2)
        writer.writerow([
            s.date.isoformat(),
            s.start_time.isoformat() if s.start_time else '',
            s.end_time.isoformat() if s.end_time else '',
            duration_hours,
            s.title,
            getattr(s.created_by, 'username', ''),
            'yes' if s.is_online else 'no',
            s.location,
            s.meeting_link or '',
            s.status,
        ])

    return response


@login_required
def group_top_members_export(request, group_id):
    """Export Top members (by hours, then sessions) for a group within date range."""
    group = get_object_or_404(StudyGroup, pk=group_id)
    if not group.members.filter(id=request.user.id).exists():
        return HttpResponse('Forbidden', status=403)

    today = timezone.localdate()
    default_end = today
    default_start = default_end - datetime.timedelta(weeks=12)

    q_from = request.GET.get('from')
    q_to = request.GET.get('to')
    preset = request.GET.get('preset')

    start_date = default_start
    end_date = default_end

    def parse_date(s):
        try:
            return datetime.date.fromisoformat(s)
        except Exception:
            return None

    presets_weeks = {'4w': 4, '8w': 8, '12w': 12, '26w': 26}
    if preset in presets_weeks:
        end_date = default_end
        start_date = end_date - datetime.timedelta(weeks=presets_weeks[preset])
    else:
        if q_from:
            pd = parse_date(q_from)
            if pd:
                start_date = pd
        if q_to:
            pd = parse_date(q_to)
            if pd:
                end_date = pd
        if start_date > end_date:
            start_date, end_date = end_date, start_date

    sessions_qs = group.studysession_set.filter(date__gte=start_date, date__lte=end_date).only('date','start_time','end_time','created_by')

    # Aggregate hours and session counts by creator
    from collections import defaultdict
    counts = defaultdict(int)
    hours = defaultdict(float)
    for s in sessions_qs:
        username = getattr(s.created_by, 'username', 'Unknown')
        counts[username] += 1
        if s.start_time and s.end_time:
            sd = datetime.datetime.combine(s.date, s.start_time)
            ed = datetime.datetime.combine(s.date, s.end_time)
            secs = max((ed - sd).total_seconds(), 0)
            hours[username] += secs / 3600.0

    rows = [{ 'user': u, 'sessions': counts[u], 'hours': round(hours[u], 2) } for u in set(list(counts.keys()) + list(hours.keys()))]
    rows.sort(key=lambda x: (-x['hours'], -x['sessions'], x['user']))

    response = HttpResponse(content_type='text/csv')
    filename = f"group_{group_id}_top_members_{start_date.isoformat()}_to_{end_date.isoformat()}.csv"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)
    writer.writerow(['user', 'sessions', 'hours'])
    for r in rows:
        writer.writerow([r['user'], r['sessions'], r['hours']])
    return response

class StudyGroupCreateView(LoginRequiredMixin, CreateView):
    model = StudyGroup
    form_class = StudyGroupForm
    template_name = 'core/group_form.html'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        GroupMembership.objects.create(
            user=self.request.user,
            group=self.object,
            role='admin'
        )
        messages.success(self.request, 'Study group created successfully!')
    
    def get_success_url(self):
        return reverse('core:group_detail', kwargs={'pk': self.object.pk})

class StudyGroupUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = StudyGroup
    form_class = StudyGroupForm
    template_name = 'core/group_form.html'

    def test_func(self):
        group = self.get_object()
        return GroupMembership.objects.filter(
            user=self.request.user, 
            group=group, 
            role='admin'
        ).exists()

    def form_valid(self, form):
        messages.success(self.request, 'Study group updated successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('core:group_detail', kwargs={'pk': self.object.pk})

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


@login_required
def profile_edit(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=profile, user=request.user)
        if form.is_valid():
            form.save(user=request.user)
            messages.success(request, 'Profile updated successfully!')
            return redirect('core:profile')
    else:
        form = ProfileEditForm(instance=profile, user=request.user)

    return render(request, 'core/profile_edit.html', {'form': form})


@user_passes_test(lambda u: u.is_authenticated and u.is_superuser, login_url='login')
def stats(request):
    """Site-wide statistics dashboard with charts (ADMIN ONLY).

    Shows totals and trends for sessions, study hours, users, and groups.
    """
    # Optional group filter and date window (presets or from/to)
    group_id = request.GET.get('group')
    current_group = None
    try:
        if group_id:
            current_group = StudyGroup.objects.get(pk=int(group_id))
    except (StudyGroup.DoesNotExist, ValueError):
        current_group = None

    # Date window
    today = timezone.localdate()
    default_end = today
    default_start = default_end - datetime.timedelta(weeks=12)
    q_from = request.GET.get('from')
    q_to = request.GET.get('to')
    preset = request.GET.get('preset')

    def parse_date(s):
        try:
            return datetime.date.fromisoformat(s)
        except Exception:
            return None

    start_date = default_start
    end_date = default_end
    presets_weeks = {'4w': 4, '8w': 8, '12w': 12, '26w': 26}
    if preset in presets_weeks:
        end_date = default_end
        start_date = end_date - datetime.timedelta(weeks=presets_weeks[preset])
    else:
        if q_from:
            pd = parse_date(q_from)
            if pd:
                start_date = pd
        if q_to:
            pd = parse_date(q_to)
            if pd:
                end_date = pd
    if start_date > end_date:
        start_date, end_date = end_date, start_date

    # Base querysets (optionally by group)
    session_base = StudySession.objects.all()
    material_base = StudyMaterial.objects.all()
    comment_base = Comment.objects.all()
    if current_group:
        session_base = session_base.filter(group=current_group)
        material_base = material_base.filter(group=current_group)
        comment_base = comment_base.filter(group=current_group)

    # Totals (respect group; sessions/materials/comments further restricted as needed)
    if current_group:
        total_users = current_group.members.count()
        total_groups = 1
    else:
        total_users = User.objects.count()
        total_groups = StudyGroup.objects.count()
    total_sessions = session_base.count()
    total_materials = material_base.count()
    total_comments = comment_base.count()

    # Total study hours in selected window (sum of durations)
    sessions = session_base.filter(date__gte=start_date, date__lte=end_date).only('date', 'start_time', 'end_time')
    total_seconds = 0
    for s in sessions:
        if s.start_time and s.end_time:
            start_dt = datetime.datetime.combine(s.date, s.start_time)
            end_dt = datetime.datetime.combine(s.date, s.end_time)
            delta = end_dt - start_dt
            if delta.total_seconds() > 0:
                total_seconds += delta.total_seconds()
    total_study_hours = round(total_seconds / 3600, 2)

    # Time window helpers
    # Weekly buckets based on selected end_date (ending week)
    week_starts = []
    current_week_start = end_date - datetime.timedelta(days=end_date.weekday())
    for i in range(11, -1, -1):
        week_starts.append(current_week_start - datetime.timedelta(weeks=i))

    week_labels = [ws.strftime('%d %b') for ws in week_starts]
    sessions_per_week = [0] * len(week_starts)
    hours_per_week = [0.0] * len(week_starts)

    start_range = week_starts[0]
    end_range = week_starts[-1] + datetime.timedelta(days=7)
    qs = session_base.filter(date__gte=start_range, date__lt=end_range).only('date', 'start_time', 'end_time')
    for s in qs:
        # find index of week bucket
        # compute the Monday of that session's week
        s_week_start = s.date - datetime.timedelta(days=s.date.weekday())
        if s_week_start in week_starts:
            idx = week_starts.index(s_week_start)
            sessions_per_week[idx] += 1
            if s.start_time and s.end_time:
                start_dt = datetime.datetime.combine(s.date, s.start_time)
                end_dt = datetime.datetime.combine(s.date, s.end_time)
                delta = end_dt - start_dt
                if delta.total_seconds() > 0:
                    hours_per_week[idx] += round(delta.total_seconds() / 3600, 2)

    # Scatter: start hour vs duration (hrs) for sessions in range
    scatter_points = []
    # Histogram: durations distribution (hrs)
    bin_edges = [0, 0.5, 1, 1.5, 2, 3, 4, 6, 1e9]  # last bin is open-ended
    hist_labels = ['0-0.5h', '0.5-1h', '1-1.5h', '1.5-2h', '2-3h', '3-4h', '4-6h', '6h+']
    hist_counts = [0] * (len(bin_edges) - 1)

    for s in qs:
        if s.start_time and s.end_time:
            start_dt = datetime.datetime.combine(s.date, s.start_time)
            end_dt = datetime.datetime.combine(s.date, s.end_time)
            secs = (end_dt - start_dt).total_seconds()
            if secs > 0:
                hours = round(secs / 3600.0, 2)
                # scatter x as decimal start hour
                x_hour = s.start_time.hour + (s.start_time.minute / 60.0)
                scatter_points.append({'x': round(x_hour, 2), 'y': hours})
                # histogram binning
                for i in range(len(bin_edges) - 1):
                    if bin_edges[i] <= hours < bin_edges[i + 1]:
                        hist_counts[i] += 1
                        break

    # New users/members per month (last 6 months)
    months = []
    month_labels = []
    today_month_start = end_date.replace(day=1)
    for i in range(5, -1, -1):
        # Compute month start by subtracting i months
        year = today_month_start.year
        month = today_month_start.month - i
        while month <= 0:
            month += 12
            year -= 1
        month_start = datetime.date(year, month, 1)
        months.append(month_start)
        month_labels.append(month_start.strftime('%b %Y'))
    # month end helper
    def next_month(d: datetime.date) -> datetime.date:
        if d.month == 12:
            return datetime.date(d.year + 1, 1, 1)
        return datetime.date(d.year, d.month + 1, 1)

    users_per_month = []
    month_series_label = 'Usuarios'
    if current_group:
        month_series_label = 'Miembros'
        for m in months:
            nm = next_month(m)
            count = GroupMembership.objects.filter(group=current_group, joined_at__date__gte=m, joined_at__date__lt=nm).count()
            users_per_month.append(count)
    else:
        for m in months:
            nm = next_month(m)
            count = User.objects.filter(date_joined__date__gte=m, date_joined__date__lt=nm).count()
            users_per_month.append(count)

    # Active users last 30 days (by last_login)
    last_30 = end_date - datetime.timedelta(days=30)
    if current_group:
        active_users_30d = User.objects.filter(last_login__date__gte=last_30, studygroup__id=current_group.id).distinct().count()
    else:
        active_users_30d = User.objects.filter(last_login__date__gte=last_30).count()

    charts = {
        'week_labels': week_labels,
        'sessions_per_week': sessions_per_week,
        'hours_per_week': [round(h, 2) for h in hours_per_week],
        'month_labels': month_labels,
        'users_per_month': users_per_month,
        'scatter_points': scatter_points,
        'hist_labels': hist_labels,
        'hist_counts': hist_counts,
    }

    context = {
        'total_users': total_users,
        'total_groups': total_groups,
        'total_sessions': total_sessions,
        'total_materials': total_materials,
        'total_comments': total_comments,
        'total_study_hours': total_study_hours,
        'active_users_30d': active_users_30d,
        'charts_json': json.dumps(charts),
        'groups': StudyGroup.objects.order_by('name').only('id', 'name'),
        'current_group': current_group,
        'filter_start': start_date.isoformat(),
        'filter_end': end_date.isoformat(),
        'filter_preset': preset or '',
        'month_series_label': month_series_label,
    }

    return render(request, 'core/stats.html', context)


@login_required
def my_stats(request):
    """Personal statistics dashboard for authenticated users.
    
    Shows user's own sessions, study hours, and statistics from their groups.
    """
    user = request.user
    
    # Date window (defaults to last 12 weeks)
    today = timezone.localdate()
    default_end = today
    default_start = default_end - datetime.timedelta(weeks=12)
    
    q_from = request.GET.get('from')
    q_to = request.GET.get('to')
    preset = request.GET.get('preset')
    
    def parse_date(s):
        try:
            return datetime.date.fromisoformat(s)
        except Exception:
            return None
    
    start_date = default_start
    end_date = default_end
    presets_weeks = {'4w': 4, '8w': 8, '12w': 12, '26w': 26}
    if preset in presets_weeks:
        end_date = default_end
        start_date = end_date - datetime.timedelta(weeks=presets_weeks[preset])
    else:
        if q_from:
            pd = parse_date(q_from)
            if pd:
                start_date = pd
        if q_to:
            pd = parse_date(q_to)
            if pd:
                end_date = pd
    if start_date > end_date:
        start_date, end_date = end_date, start_date
    
    # Get user's groups
    user_groups = StudyGroup.objects.filter(members=user)
    
    # Sessions created by this user
    my_sessions = StudySession.objects.filter(created_by=user)
    total_my_sessions = my_sessions.count()
    
    # Sessions in user's groups (not just created by user)
    group_sessions = StudySession.objects.filter(group__in=user_groups)
    
    # Total study hours for user's own sessions in date range
    sessions_range = my_sessions.filter(date__gte=start_date, date__lte=end_date).only('date', 'start_time', 'end_time')
    total_seconds = 0
    for s in sessions_range:
        if s.start_time and s.end_time:
            start_dt = datetime.datetime.combine(s.date, s.start_time)
            end_dt = datetime.datetime.combine(s.date, s.end_time)
            delta = end_dt - start_dt
            if delta.total_seconds() > 0:
                total_seconds += delta.total_seconds()
    my_study_hours = round(total_seconds / 3600, 2)
    
    # Weekly data for user's sessions
    week_starts = []
    current_week_start = end_date - datetime.timedelta(days=end_date.weekday())
    for i in range(11, -1, -1):
        week_starts.append(current_week_start - datetime.timedelta(weeks=i))
    
    week_labels = [ws.strftime('%d %b') for ws in week_starts]
    my_sessions_per_week = [0] * len(week_starts)
    my_hours_per_week = [0.0] * len(week_starts)
    
    start_range = week_starts[0]
    end_range = week_starts[-1] + datetime.timedelta(days=7)
    qs = my_sessions.filter(date__gte=start_range, date__lt=end_range).only('date', 'start_time', 'end_time')
    
    for s in qs:
        s_week_start = s.date - datetime.timedelta(days=s.date.weekday())
        if s_week_start in week_starts:
            idx = week_starts.index(s_week_start)
            my_sessions_per_week[idx] += 1
            if s.start_time and s.end_time:
                start_dt = datetime.datetime.combine(s.date, s.start_time)
                end_dt = datetime.datetime.combine(s.date, s.end_time)
                delta = end_dt - start_dt
                if delta.total_seconds() > 0:
                    my_hours_per_week[idx] += round(delta.total_seconds() / 3600, 2)
    
    # Scatter and histogram for user's sessions
    scatter_points = []
    bin_edges = [0, 0.5, 1, 1.5, 2, 3, 4, 6, 1e9]
    hist_labels = ['0-0.5h', '0.5-1h', '1-1.5h', '1.5-2h', '2-3h', '3-4h', '4-6h', '6h+']
    hist_counts = [0] * (len(bin_edges) - 1)
    
    for s in qs:
        if s.start_time and s.end_time:
            start_dt = datetime.datetime.combine(s.date, s.start_time)
            end_dt = datetime.datetime.combine(s.date, s.end_time)
            secs = (end_dt - start_dt).total_seconds()
            if secs > 0:
                hours = round(secs / 3600.0, 2)
                x_hour = s.start_time.hour + (s.start_time.minute / 60.0)
                scatter_points.append({'x': round(x_hour, 2), 'y': hours})
                for i in range(len(bin_edges) - 1):
                    if bin_edges[i] <= hours < bin_edges[i + 1]:
                        hist_counts[i] += 1
                        break
    
    # Group breakdown (sessions per group)
    group_breakdown = []
    for grp in user_groups:
        count = my_sessions.filter(group=grp).count()
        if count > 0:
            group_breakdown.append({'group': grp.name, 'sessions': count})
    group_breakdown.sort(key=lambda x: -x['sessions'])
    
    charts = {
        'week_labels': week_labels,
        'sessions_per_week': my_sessions_per_week,
        'hours_per_week': [round(h, 2) for h in my_hours_per_week],
        'scatter_points': scatter_points,
        'hist_labels': hist_labels,
        'hist_counts': hist_counts,
        'group_labels': [g['group'] for g in group_breakdown],
        'group_sessions': [g['sessions'] for g in group_breakdown],
    }
    
    context = {
        'total_my_sessions': total_my_sessions,
        'my_study_hours': my_study_hours,
        'total_groups': user_groups.count(),
        'charts_json': json.dumps(charts),
        'filter_start': start_date.isoformat(),
        'filter_end': end_date.isoformat(),
        'filter_preset': preset or '',
    }
    
    return render(request, 'core/my_stats.html', context)


@user_passes_test(lambda u: u.is_authenticated and u.is_superuser, login_url='login')
def stats_export(request):
    """Export sessions as CSV for global or selected group within the chosen date range (ADMIN ONLY)."""
    group_id = request.GET.get('group')
    current_group = None
    try:
        if group_id:
            current_group = StudyGroup.objects.get(pk=int(group_id))
    except (StudyGroup.DoesNotExist, ValueError):
        current_group = None

    today = timezone.localdate()
    default_end = today
    default_start = default_end - datetime.timedelta(weeks=12)

    q_from = request.GET.get('from')
    q_to = request.GET.get('to')
    preset = request.GET.get('preset')

    def parse_date(s):
        try:
            return datetime.date.fromisoformat(s)
        except Exception:
            return None

    start_date = default_start
    end_date = default_end
    presets_weeks = {'4w': 4, '8w': 8, '12w': 12, '26w': 26}
    if preset in presets_weeks:
        end_date = default_end
        start_date = end_date - datetime.timedelta(weeks=presets_weeks[preset])
    else:
        if q_from:
            pd = parse_date(q_from)
            if pd:
                start_date = pd
        if q_to:
            pd = parse_date(q_to)
            if pd:
                end_date = pd
    if start_date > end_date:
        start_date, end_date = end_date, start_date

    session_base = StudySession.objects.all()
    if current_group:
        session_base = session_base.filter(group=current_group)
    sessions_qs = session_base.filter(date__gte=start_date, date__lte=end_date).order_by('date', 'start_time')

    response = HttpResponse(content_type='text/csv')
    base = f"global" if not current_group else f"group_{current_group.id}"
    filename = f"{base}_sessions_{start_date.isoformat()}_to_{end_date.isoformat()}.csv"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    import csv as _csv
    writer = _csv.writer(response)
    writer.writerow(['date', 'start_time', 'end_time', 'duration_hours', 'title', 'created_by', 'group', 'is_online', 'location', 'meeting_link', 'status'])

    for s in sessions_qs:
        duration_hours = ''
        if s.start_time and s.end_time:
            start_dt = datetime.datetime.combine(s.date, s.start_time)
            end_dt = datetime.datetime.combine(s.date, s.end_time)
            secs = max((end_dt - start_dt).total_seconds(), 0)
            duration_hours = round(secs / 3600.0, 2)
        writer.writerow([
            s.date.isoformat(),
            s.start_time.isoformat() if s.start_time else '',
            s.end_time.isoformat() if s.end_time else '',
            duration_hours,
            s.title,
            getattr(s.created_by, 'username', ''),
            getattr(s.group, 'name', ''),
            'yes' if s.is_online else 'no',
            s.location,
            s.meeting_link or '',
            s.status,
        ])

    return response


@user_passes_test(lambda u: u.is_authenticated and u.is_superuser, login_url='login')
def stats_top_members_export(request):
    """Export Top members CSV for the selected group within date range (ADMIN ONLY); requires group param."""
    group_id = request.GET.get('group')
    if not group_id:
        return HttpResponse('Group parameter required', status=400)
    try:
        group = StudyGroup.objects.get(pk=int(group_id))
    except (StudyGroup.DoesNotExist, ValueError):
        return HttpResponse('Invalid group', status=400)

    today = timezone.localdate()
    default_end = today
    default_start = default_end - datetime.timedelta(weeks=12)

    q_from = request.GET.get('from')
    q_to = request.GET.get('to')
    preset = request.GET.get('preset')

    start_date = default_start
    end_date = default_end

    def parse_date(s):
        try:
            return datetime.date.fromisoformat(s)
        except Exception:
            return None

    presets_weeks = {'4w': 4, '8w': 8, '12w': 12, '26w': 26}
    if preset in presets_weeks:
        end_date = default_end
        start_date = end_date - datetime.timedelta(weeks=presets_weeks[preset])
    else:
        if q_from:
            pd = parse_date(q_from)
            if pd:
                start_date = pd
        if q_to:
            pd = parse_date(q_to)
            if pd:
                end_date = pd
        if start_date > end_date:
            start_date, end_date = end_date, start_date

    sessions_qs = group.studysession_set.filter(date__gte=start_date, date__lte=end_date).only('date','start_time','end_time','created_by')

    from collections import defaultdict
    counts = defaultdict(int)
    hours = defaultdict(float)
    for s in sessions_qs:
        username = getattr(s.created_by, 'username', 'Unknown')
        counts[username] += 1
        if s.start_time and s.end_time:
            sd = datetime.datetime.combine(s.date, s.start_time)
            ed = datetime.datetime.combine(s.date, s.end_time)
            secs = max((ed - sd).total_seconds(), 0)
            hours[username] += secs / 3600.0

    rows = [{ 'user': u, 'sessions': counts[u], 'hours': round(hours[u], 2) } for u in set(list(counts.keys()) + list(hours.keys()))]
    rows.sort(key=lambda x: (-x['hours'], -x['sessions'], x['user']))

    response = HttpResponse(content_type='text/csv')
    filename = f"group_{group.id}_top_members_{start_date.isoformat()}_to_{end_date.isoformat()}.csv"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)
    writer.writerow(['user', 'sessions', 'hours'])
    for r in rows:
        writer.writerow([r['user'], r['sessions'], r['hours']])
    return response

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

# Study Session views
class StudySessionCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = StudySession
    form_class = StudySessionForm
    template_name = 'core/session_form.html'

    def test_func(self):
        group = get_object_or_404(StudyGroup, pk=self.kwargs['group_id'])
        return GroupMembership.objects.filter(
            user=self.request.user,
            group=group,
            role__in=['admin', 'moderator']
        ).exists()

    def form_valid(self, form):
        form.instance.group_id = self.kwargs['group_id']
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Study session created successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('core:group_detail', kwargs={'pk': self.kwargs['group_id']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group'] = get_object_or_404(StudyGroup, pk=self.kwargs['group_id'])
        return context

class StudySessionUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = StudySession
    form_class = StudySessionForm
    template_name = 'core/session_form.html'

    def test_func(self):
        session = self.get_object()
        return (session.created_by == self.request.user or 
                GroupMembership.objects.filter(
                    user=self.request.user,
                    group=session.group,
                    role__in=['admin', 'moderator']
                ).exists())

    def form_valid(self, form):
        messages.success(self.request, 'Study session updated successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('core:group_detail', kwargs={'pk': self.object.group.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group'] = self.object.group
        return context

class StudySessionDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = StudySession
    template_name = 'core/session_confirm_delete.html'

    def test_func(self):
        session = self.get_object()
        return (session.created_by == self.request.user or 
                GroupMembership.objects.filter(
                    user=self.request.user,
                    group=session.group,
                    role='admin'
                ).exists())

    def get_success_url(self):
        messages.success(self.request, 'Study session deleted successfully!')
        return reverse('core:group_detail', kwargs={'pk': self.object.group.pk})

# Study Material views
class StudyMaterialCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = StudyMaterial
    form_class = StudyMaterialForm
    template_name = 'core/material_form.html'

    def test_func(self):
        group = get_object_or_404(StudyGroup, pk=self.kwargs['group_id'])
        return GroupMembership.objects.filter(
            user=self.request.user,
            group=group
        ).exists()

    def form_valid(self, form):
        form.instance.group_id = self.kwargs['group_id']
        form.instance.uploaded_by = self.request.user
        messages.success(self.request, 'Study material uploaded successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('core:group_detail', kwargs={'pk': self.kwargs['group_id']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group'] = get_object_or_404(StudyGroup, pk=self.kwargs['group_id'])
        return context

class StudyMaterialUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = StudyMaterial
    form_class = StudyMaterialForm
    template_name = 'core/material_form.html'

    def test_func(self):
        material = self.get_object()
        return (material.uploaded_by == self.request.user or 
                GroupMembership.objects.filter(
                    user=self.request.user,
                    group=material.group,
                    role__in=['admin', 'moderator']
                ).exists())

    def form_valid(self, form):
        messages.success(self.request, 'Study material updated successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('core:group_detail', kwargs={'pk': self.object.group.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group'] = self.object.group
        return context

class StudyMaterialDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = StudyMaterial
    template_name = 'core/material_confirm_delete.html'

    def test_func(self):
        material = self.get_object()
        return (material.uploaded_by == self.request.user or 
                GroupMembership.objects.filter(
                    user=self.request.user,
                    group=material.group,
                    role='admin'
                ).exists())

    def get_success_url(self):
        messages.success(self.request, 'Study material deleted successfully!')
        return reverse('core:group_detail', kwargs={'pk': self.object.group.pk})

# Member management views
@login_required
def change_member_role(request, group_id, membership_id):
    group = get_object_or_404(StudyGroup, pk=group_id)
    membership = get_object_or_404(GroupMembership, pk=membership_id, group=group)
    
    # Check if user is admin
    if not GroupMembership.objects.filter(user=request.user, group=group, role='admin').exists():
        messages.error(request, 'Only group admins can change member roles.')
        return redirect('core:group_detail', pk=group_id)
    
    if request.method == 'POST':
        new_role = request.POST.get('role')
        if new_role in ['member', 'moderator', 'admin']:
            # Prevent removing last admin
            if membership.role == 'admin' and new_role != 'admin':
                admin_count = GroupMembership.objects.filter(group=group, role='admin').count()
                if admin_count <= 1:
                    messages.error(request, 'Cannot remove the last admin. Promote another member first.')
                    return redirect('core:group_detail', pk=group_id)
            
            membership.role = new_role
            membership.save()
            messages.success(request, f'{membership.user.username} role updated to {new_role}.')
        else:
            messages.error(request, 'Invalid role.')
    
    return redirect('core:group_detail', pk=group_id)

@login_required
def remove_member(request, group_id, membership_id):
    group = get_object_or_404(StudyGroup, pk=group_id)
    membership = get_object_or_404(GroupMembership, pk=membership_id, group=group)
    
    # Check if user is admin
    if not GroupMembership.objects.filter(user=request.user, group=group, role='admin').exists():
        messages.error(request, 'Only group admins can remove members.')
        return redirect('core:group_detail', pk=group_id)
    
    # Prevent removing last admin
    if membership.role == 'admin':
        admin_count = GroupMembership.objects.filter(group=group, role='admin').count()
        if admin_count <= 1:
            messages.error(request, 'Cannot remove the last admin.')
            return redirect('core:group_detail', pk=group_id)
    
    if request.method == 'POST':
        username = membership.user.username
        membership.delete()
        messages.success(request, f'{username} has been removed from the group.')
    
    return redirect('core:group_detail', pk=group_id)