from django.contrib.auth import login
from django.db import transaction
from django.urls import reverse_lazy
from django.views.generic import CreateView

from apps.home.models import Membership, Workspace

from .forms import RegisterForm


class RegisterView(CreateView):
    template_name = 'register/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('home:home')

    def form_valid(self, form):
        with transaction.atomic():
            response = super().form_valid(form)  # saves the User -> self.object
            user = self.object
            display_name = form.cleaned_data.get('display_name')
            if display_name:
                user.profile.display_name = display_name
                user.profile.save(update_fields=['display_name'])

            workspace = Workspace.objects.create(
                name=form.cleaned_data['workspace_name'],
                owner=user,
            )
            Membership.objects.create(
                user=user,
                workspace=workspace,
                role=Membership.Role.OWNER,
            )
        login(self.request, user)
        return response
