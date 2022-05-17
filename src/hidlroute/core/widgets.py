from django.contrib.admin.widgets import AdminRadioSelect


class ServerRadioSelect(AdminRadioSelect):
    template_name = "admin/widgets/server-type-select.html"
    option_template_name = "admin/widgets/server-type-select-option.html"