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
from typing import TYPE_CHECKING, Callable, Dict, Union

from django.utils.module_loading import import_string

if TYPE_CHECKING:
    from hidlroute.core.service.ip_allocation import IPAllocationService

__all__ = ["service_factory"]

_SERVICE_METHOD_MARK = "_service_method"

LOGGER = logging.getLogger("hidl_core.factory")


class _ServiceFactory(object):
    def __init__(self) -> None:
        self.__cache: Dict[str, Callable] = {}

    def bootstrap(self):
        LOGGER.info("Bootstrapping HidlCore factory:")
        for prop_name in dir(self):
            prop_or_method = getattr(self, prop_name)
            if hasattr(prop_or_method, _SERVICE_METHOD_MARK):
                LOGGER.info("Determining implementation for {}".format(prop_name))
                self._invoke_prop_or_method(prop_or_method)
        LOGGER.info("HidlCore factory bootstrap finished")

    def _invoke_prop_or_method(self, prop_or_method: Union[property, Callable]):
        if isinstance(prop_or_method, property):
            return prop_or_method.fget(self)
        elif isinstance(prop_or_method, Callable):
            return prop_or_method(self)
        raise ValueError("prop_or_method must be either property or method. {} given.".format(type(prop_or_method)))

    @classmethod
    def __class_from_str(cls, class_full_name: str) -> type:
        LOGGER.info("\t Loading {}".format(class_full_name))
        return import_string(class_full_name)

    def _cached_service(service_method):
        def wrapper(self):
            if isinstance(service_method, property):
                method_name = str(id(service_method))
            elif isinstance(service_method, Callable):
                method_name = service_method.__name__
            else:
                raise ValueError("_register_service decorator must be applied either on method or property")

            if method_name not in self.__cache:
                result = self._invoke_prop_or_method(service_method)
                self.__cache[method_name] = result

            return self.__cache[method_name]

        setattr(wrapper, _SERVICE_METHOD_MARK, True)
        return property(wrapper)

    @_cached_service
    def ip_allocation_service(self) -> "IPAllocationService":
        IPAllocationService = self.__class_from_str("hidlroute.core.service.ip_allocation.IPAllocationService")
        return IPAllocationService()


service_factory = _ServiceFactory()