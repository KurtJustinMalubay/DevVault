from django.contrib.auth.views import LoginView
from django.urls import reverse

from apps.user_settings.models import UserSettings
from .forms import StyledAuthenticationForm


class DevVaultLoginView(LoginView):
    template_name = 'login/login.html'
    authentication_form = StyledAuthenticationForm
    redirect_authenticated_user = True

    def get_default_redirect_url(self):
        user_settings = getattr(self.request.user, 'settings', None)
        if user_settings and user_settings.default_landing_page == UserSettings.LandingPage.ENTRIES:
            return reverse('home:entries')
        return super().get_default_redirect_url()
