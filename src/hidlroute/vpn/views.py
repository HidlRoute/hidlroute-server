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

from django.contrib.auth.mixins import AccessMixin
from django.views import View

from hidlroute.core.models import Person


class OwnDeviceCheckMixin(AccessMixin):
    """
    Checks that device which is being edited belongs to the user who edits it.
    """

    def dispatch(self, request, *args, **kwargs):
        member = args[0].server_to_member.member.get_real_instance()
        if not isinstance(member, Person):
            return self.handle_no_permission()
        if not member.user == self.request.user:
            return self.handle_no_permission()

        return super().dispatch(request, *args, **kwargs)


class BaseVPNDeviceConfigView(OwnDeviceCheckMixin, View):
    def post(self, request, device):
        raise NotImplementedError
