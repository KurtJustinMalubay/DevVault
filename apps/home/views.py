from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Count, Q, Subquery
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView

from .forms import CommentForm, EntryForm, WorkspaceForm, WorkspaceInviteForm
from .models import Comment, Entry, Membership, Workspace
from .workspaces import get_active_workspace


class WorkspaceAccessMixin(LoginRequiredMixin):
    def get_workspace(self):
        return get_active_workspace(self.request)

    def get_entry(self):
        return get_object_or_404(
            Entry.objects.select_related('author', 'workspace').prefetch_related('tags', 'comments__author'),
            pk=self.kwargs['pk'],
            workspace__members=self.request.user,
        )


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'home/home.html'

    def _active_workspace(self):
        return get_active_workspace(self.request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        workspace = self._active_workspace()
        context['workspace'] = workspace
        context['user_settings'] = getattr(self.request.user, 'settings', None)

        if workspace is None:
            context.update({
                'recent_entries': [],
                'open_bugs': [],
                'total_assets': 0,
                'open_issue_count': 0,
                'total_entries': 0,
                'member_count': 0,
            })
            return context

        entries = Entry.objects.filter(workspace=workspace).select_related(
            'author',
            'author__profile',
            'workspace',
        )

        context['recent_entries'] = entries[:6]
        context['open_bugs'] = entries.filter(
            entry_type=Entry.EntryType.BUG,
        ).exclude(status=Entry.Status.RESOLVED)[:5]

        stats = entries.aggregate(
            total_assets=Count('pk', filter=Q(entry_type=Entry.EntryType.ASSET)),
            open_issue_count=Count(
                'pk',
                filter=Q(entry_type=Entry.EntryType.BUG) & ~Q(status=Entry.Status.RESOLVED),
            ),
            total_entries=Count('pk'),
            in_progress_count=Count(
                'pk',
                filter=Q(status=Entry.Status.IN_PROGRESS),
            ),
            resolved_count=Count(
                'pk',
                filter=Q(status=Entry.Status.RESOLVED),
            ),
        )
        context.update(stats)
        context['progress_percent'] = (
            round((context['resolved_count'] / context['total_entries']) * 100)
            if context['total_entries']
            else 0
        )
        context['member_count'] = Membership.objects.filter(workspace=workspace).count()

        return context


class WorkspaceSwitchView(LoginRequiredMixin, TemplateView):
    def post(self, request, *args, **kwargs):
        workspace = get_object_or_404(Workspace, pk=request.POST.get('workspace_id'), members=request.user)
        request.session['active_workspace_id'] = workspace.pk
        next_url = request.POST.get('next', '')
        if next_url and url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            return redirect(next_url)
        return redirect('home:home')


class WorkspaceCreateView(LoginRequiredMixin, CreateView):
    form_class = WorkspaceForm
    template_name = 'home/workspace_form.html'

    def form_valid(self, form):
        with transaction.atomic():
            workspace = form.save(commit=False)
            workspace.owner = self.request.user
            workspace.save()
            Membership.objects.create(
                user=self.request.user,
                workspace=workspace,
                role=Membership.Role.OWNER,
            )
        self.request.session['active_workspace_id'] = workspace.pk
        messages.success(self.request, 'Vault created.')
        return redirect('home:home')


@login_required
def workspace_invite_view(request):
    workspace = get_active_workspace(request)
    if workspace is None:
        messages.error(request, 'Choose or create a vault before inviting members.')
        return redirect('home:home')
    membership = get_object_or_404(Membership, workspace=workspace, user=request.user)
    if membership.role != Membership.Role.OWNER:
        messages.error(request, 'Only the vault owner can invite members.')
        return redirect('home:home')
    if request.method == 'POST':
        form = WorkspaceInviteForm(request.POST)
        if form.is_valid():
            invitee = form.cleaned_data['invitee']
            with transaction.atomic():
                # Serialize invitations per vault so simultaneous requests cannot
                # both pass the five-member limit based on a stale count.
                workspace = Workspace.objects.select_for_update().get(pk=workspace.pk)
                if invitee == request.user:
                    form.add_error('identifier', 'You are already in this vault.')
                elif Membership.objects.filter(workspace=workspace, user=invitee).exists():
                    form.add_error('identifier', 'That user is already a member.')
                elif workspace.member_count >= 5:
                    form.add_error('identifier', 'This vault already has five members.')
                else:
                    Membership.objects.create(
                        user=invitee,
                        workspace=workspace,
                        role=Membership.Role.MEMBER,
                    )
            if not form.errors:
                messages.success(request, f'{invitee.username} joined {workspace.name}.')
                return redirect('home:workspace-invite')
    else:
        form = WorkspaceInviteForm()
    return render(request, 'home/workspace_invite.html', {'form': form, 'workspace': workspace})


class EntryListView(WorkspaceAccessMixin, ListView):
    template_name = 'home/entries.html'
    context_object_name = 'entries'
    paginate_by = 12

    def get_queryset(self):
        workspace = self.get_workspace()
        if workspace is None:
            return Entry.objects.none()

        queryset = Entry.objects.filter(
            workspace=workspace,
        ).select_related(
            'author',
            'author__profile',
            'workspace',
        ).prefetch_related('tags')

        query = self.request.GET.get('q', '').strip()
        entry_type = self.request.GET.get('type', '').strip()
        status = self.request.GET.get('status', '').strip()
        commented = self.request.GET.get('commented', '').strip()
        if query:
            queryset = queryset.filter(Q(title__icontains=query) | Q(description__icontains=query))
        if entry_type in Entry.EntryType.values:
            queryset = queryset.filter(entry_type=entry_type)
        if status in Entry.Status.values:
            queryset = queryset.filter(status=status)
        print("\n=== DJANGO ORM JOIN SQL ===")
        print(queryset.query)

        if commented == '1':
            commented_entry_ids = Comment.objects.filter(
                entry__workspace=workspace,
            ).values('entry_id')
            queryset = queryset.filter(id__in=Subquery(commented_entry_ids))
            print("\n=== DJANGO ORM SUBQUERY SQL ===")
            print(queryset.query)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['workspace'] = self.get_workspace()
        context['query'] = self.request.GET.get('q', '').strip()
        context['selected_type'] = self.request.GET.get('type', '')
        context['selected_status'] = self.request.GET.get('status', '')
        context['selected_commented'] = self.request.GET.get('commented', '').strip()
        context['entry_types'] = Entry.EntryType.choices
        context['statuses'] = Entry.Status.choices
        return context


class EntryDetailView(WorkspaceAccessMixin, DetailView):
    template_name = 'home/entry_detail.html'
    context_object_name = 'entry'

    def get_object(self, queryset=None):
        return self.get_entry()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault('comment_form', CommentForm())
        return context

    def post(self, request, *args, **kwargs):
        entry = self.get_object()
        self.object = entry
        form = CommentForm(request.POST)
        if form.is_valid():
            Comment.objects.create(entry=entry, author=request.user, body=form.cleaned_data['body'])
            messages.success(request, 'Comment added.')
            return redirect(entry)
        return self.render_to_response(self.get_context_data(comment_form=form))


class EntryCreateView(WorkspaceAccessMixin, CreateView):
    template_name = 'home/entry_form.html'
    form_class = EntryForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and self.get_workspace() is None:
            messages.error(request, 'Create or join a vault before adding entries.')
            return redirect('home:home')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.workspace = self.get_workspace()
        form.instance.author = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Entry created.')
        return response


class EntryUpdateView(WorkspaceAccessMixin, UpdateView):
    template_name = 'home/entry_form.html'
    form_class = EntryForm

    def get_object(self, queryset=None):
        return self.get_entry()

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Entry updated.')
        return response


class EntryDeleteView(WorkspaceAccessMixin, DeleteView):
    template_name = 'home/entry_confirm_delete.html'
    success_url = reverse_lazy('home:entries')

    def get_object(self, queryset=None):
        return self.get_entry()

    def form_valid(self, form):
        messages.success(self.request, 'Entry deleted.')
        return super().form_valid(form)
