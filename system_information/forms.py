import signal
from django import forms

# http://www.kernel.org/doc/man-pages/online/pages/man7/signal.7.html
SIGNAL_CHOICES = (
    (signal.SIGTERM, "Termination (%s)" % signal.SIGTERM),
    (signal.SIGKILL, "Kill (%s)" % signal.SIGKILL),
)


class KillForm(forms.Form):
    pid = forms.IntegerField(widget=forms.widgets.HiddenInput())
    sig = forms.ChoiceField(label="signal", choices=SIGNAL_CHOICES)
