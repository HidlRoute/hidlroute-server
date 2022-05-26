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

from defender.utils import get_blocked_ips, get_blocked_usernames, unblock_ip, unblock_username
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse


@permission_required("hidl_auth.can_manage_defender")
def block_view(request):
    """List the blocked IP and Usernames"""
    blocked_ip_list = get_blocked_ips()
    blocked_username_list = get_blocked_usernames()

    context = {
        "blocked_ip_list": blocked_ip_list,
        "blocked_username_list": blocked_username_list,
    }
    return render(request, "defender/admin/blocks.html", context)


@permission_required("hidl_auth.can_manage_defender")
def unblock_ip_view(request, ip_address):
    """upblock the given ip"""
    if request.method == "POST":
        unblock_ip(ip_address)
    return HttpResponseRedirect(reverse("defender:blocks"))


@permission_required("hidl_auth.can_manage_defender")
def unblock_username_view(request, username):
    """unblockt he given username"""
    if request.method == "POST":
        unblock_username(username)
    return HttpResponseRedirect(reverse("defender:blocks"))
