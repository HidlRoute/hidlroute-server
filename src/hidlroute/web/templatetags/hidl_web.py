from typing import List, Dict

from django.template import Library
from django.contrib import admin
from hidlroute.core import models as models_core

register = Library()


@register.filter
def filter_child_models(apps: List[Dict]) -> List[Dict]:
    target = (models_core.Server, models_core.Device)
    for app in apps:
        app["models"] = list(
            filter(lambda x: not (issubclass(x['model'], target) and x['model'] not in target), app["models"])
        )
    return list(filter(lambda x: len(x["models"]) > 0, apps))
