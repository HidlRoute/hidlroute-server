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

from django.urls import path, re_path
from .views_defender import block_view, unblock_ip_view, unblock_username_view

app_name = "hidl_web"
urlpatterns = [
    path("blocks/", block_view, name="blocks"),
    re_path(
        "blocks/ip/(?P<ip_address>[A-Za-z0-9-._]+)/unblock",
        unblock_ip_view,
        name="unblock_ip",
    ),
    path(
        "blocks/username/<path:username>/unblock",
        unblock_username_view,
        name="unblock_username",
    ),
]
