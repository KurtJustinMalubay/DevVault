from django.urls import path

from . import views

app_name = 'home'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('workspaces/switch/', views.WorkspaceSwitchView.as_view(), name='workspace-switch'),
    path('workspaces/new/', views.WorkspaceCreateView.as_view(), name='workspace-create'),
    path('workspaces/invite/', views.workspace_invite_view, name='workspace-invite'),
    path('entries/', views.EntryListView.as_view(), name='entries'),
    path('entries/new/', views.EntryCreateView.as_view(), name='entry-create'),
    path('entries/<int:pk>/', views.EntryDetailView.as_view(), name='entry-detail'),
    path('entries/<int:pk>/edit/', views.EntryUpdateView.as_view(), name='entry-edit'),
    path('entries/<int:pk>/delete/', views.EntryDeleteView.as_view(), name='entry-delete'),
]
