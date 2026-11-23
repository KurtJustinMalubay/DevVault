from .models import Workspace


def get_user_workspaces(request):
    workspaces = getattr(request, '_devvault_user_workspaces', None)
    if workspaces is None:
        workspaces = list(
            Workspace.objects.filter(members=request.user).only('id', 'name')
        )
        request._devvault_user_workspaces = workspaces
    return workspaces


def get_active_workspace(request):
    if hasattr(request, '_devvault_active_workspace'):
        return request._devvault_active_workspace

    workspaces = get_user_workspaces(request)
    active_id = request.session.get('active_workspace_id')
    workspace = next((item for item in workspaces if item.pk == active_id), None)
    if workspace is None and workspaces:
        workspace = workspaces[0]
        request.session['active_workspace_id'] = workspace.pk

    request._devvault_active_workspace = workspace
    return workspace
