#    Hidl Route - opensource vpn management system
#    Copyright (C) 2023 Dmitry Berezovsky, Alexander Cherednichenko
#
#    Hidl Route is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Hidl Route is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
from typing import Callable, Dict, Union, Any, Optional, TypeVar

from django.utils.module_loading import import_string

from hidlroute.core.service.base import WorkerService
from hidlroute.core.service.firewall.base import FirewallService
from hidlroute.core.service.networking.base import NetworkingService

__all__ = ["default_service_factory", "ServiceFactory", "cached_service"]

_SERVICE_METHOD_MARK = "_service_method"

LOGGER = logging.getLogger("hidl_core.factory")

T = TypeVar("T")


def cached_service(service_method: Callable[[Any], T], override=True):
    def wrapper(self) -> T:
        if isinstance(service_method, property):
            method_name = str(id(service_method))
        elif isinstance(service_method, Callable):
            method_name = service_method.__name__
        else:
            raise ValueError("_register_service decorator must be applied either on method or property")

        from_cache = self._get_from_cache(method_name, not override)
        if from_cache is None:
            result = self._invoke_prop_or_method(service_method)
            self.cache[method_name] = result

        return self.cache[method_name]

    setattr(wrapper, _SERVICE_METHOD_MARK, True)
    return property(wrapper)


class ServiceFactory(object):
    def __init__(self, parent: "ServiceFactory" = None) -> None:
        self.cache: Dict[str, Callable] = {}
        self.parent_cache = parent.cache if parent is not None else {}

    def bootstrap(self):
        factory_name = self.__class__.__name__
        LOGGER.info(f"Bootstrapping {factory_name} factory:")
        for prop_name in dir(self):
            prop_or_method = getattr(self, prop_name)
            if hasattr(prop_or_method, _SERVICE_METHOD_MARK):
                LOGGER.info("Determining implementation for {}".format(prop_name))
                self._invoke_prop_or_method(prop_or_method)
        LOGGER.info(f"{factory_name} factory bootstrap finished")

    def reset_cache(self):
        self.cache.clear()

    def _invoke_prop_or_method(self, prop_or_method: Union[property, Callable]):
        if isinstance(prop_or_method, property):
            return prop_or_method.fget(self)
        elif isinstance(prop_or_method, Callable):
            return prop_or_method(self)
        raise ValueError("prop_or_method must be either property or method. {} given.".format(type(prop_or_method)))

    @classmethod
    def _class_from_str(cls, class_full_name: str) -> type:
        LOGGER.info("\t Loading {}".format(class_full_name))
        return import_string(class_full_name)

    @classmethod
    def _instance_from_str(cls, class_full_name: str) -> Any:
        return cls._class_from_str(class_full_name)()

    def _get_from_cache(self, identity: str, consider_parent=True) -> Optional[Callable]:
        if identity in self.cache:
            return self.cache[identity]
        if consider_parent:
            return self.parent_cache.get(identity)
        return None

    @cached_service
    def networking_service(self) -> NetworkingService:
        return self._instance_from_str("hidlroute.core.service.networking.pyroute2.PyRoute2NetworkingService")

    @cached_service
    def firewall_service(self) -> FirewallService:
        return self._instance_from_str("hidlroute.core.service.firewall.iptables.IpTablesFirewallService")

    @cached_service
    def worker_service(self) -> WorkerService:
        # return self._instance_from_str("hidlroute.core.service.worker.SynchronousWorkerService")
        return self._instance_from_str("hidlroute.core.service.worker.CeleryWorkerService")


default_service_factory = ServiceFactory()
