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

from defender.decorators import watch_login as defender_watch_login
from django.utils.decorators import method_decorator
from two_factor.views import LoginView


class PreventBruteforceOnLoginMiddleware:
    """Failed login middleware"""

    patched = False

    def __init__(self, get_response):
        self.get_response = get_response

        # Watch the auth login.
        # Monkey-patch only once - otherwise we would be recording
        # failed attempts multiple times!
        if not self.__class__.patched:
            our_decorator = defender_watch_login()
            watch_login_method = method_decorator(our_decorator)
            LoginView.dispatch = watch_login_method(LoginView.dispatch)

            self.__class__.patched = True

    def __call__(self, request):
        response = self.get_response(request)
        return response
