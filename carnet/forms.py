from django.contrib.auth.forms import AuthenticationForm


class BootstrapAuthenticationForm(AuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)

        self.fields['username'].widget.attrs['placeholder'] = self.fields['username'].label
        self.fields['username'].widget.attrs['autofocus'] = True

        self.fields['password'].widget.attrs['placeholder'] = self.fields['password'].label
