from apps.home.models import Workspace


def workspace_context(request):
    if not request.user.is_authenticated:
        return {}
    workspaces = list(Workspace.objects.filter(members=request.user))
    active_id = request.session.get('active_workspace_id')
    active_workspace = next((workspace for workspace in workspaces if workspace.pk == active_id), None)
    if active_workspace is None and workspaces:
        active_workspace = workspaces[0]
        request.session['active_workspace_id'] = active_workspace.pk
    return {
        'user_workspaces': workspaces,
        'active_workspace': active_workspace,
        'user_settings': getattr(request.user, 'settings', None),
    }
