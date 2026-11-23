from apps.home.workspaces import get_active_workspace, get_user_workspaces


def workspace_context(request):
    if not request.user.is_authenticated:
        return {}
    workspaces = get_user_workspaces(request)
    active_workspace = get_active_workspace(request)
    return {
        'user_workspaces': workspaces,
        'active_workspace': active_workspace,
        'user_settings': getattr(request.user, 'settings', None),
    }
