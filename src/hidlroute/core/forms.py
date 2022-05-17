from polymorphic.admin import PolymorphicModelChoiceForm
from django.utils.translation import gettext_lazy as _
from django import forms

from hidlroute.core.widgets import ServerRadioSelect


class ServerTypeSelectForm(PolymorphicModelChoiceForm):
    type_label = _("Server Type")

    ct_id = forms.ChoiceField(
        label=type_label, widget=ServerRadioSelect(attrs={"class": "radiolist server-type-select"})
    )

