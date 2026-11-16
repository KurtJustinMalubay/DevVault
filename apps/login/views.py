from django.contrib.auth.views import LoginView

from .forms import StyledAuthenticationForm


class DevVaultLoginView(LoginView):
    template_name = 'login/login.html'
    authentication_form = StyledAuthenticationForm
    redirect_authenticated_user = True
