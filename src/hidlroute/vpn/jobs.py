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

from celery import shared_task

from hidlroute.vpn import const
from hidlroute.vpn.models import VpnServer

LOGGER = logging.getLogger("hidl_vpn.jobs")


@shared_task(name=const.JOB_ID_GET_VPN_SERVER_STATUS)
def get_server_status(server_id: int) -> dict:
    server = VpnServer.objects.get(pk=server_id)
    return server.vpn_service.do_get_status(server).to_dict()


@shared_task(name=const.JOB_ID_START_VPN_SERVER)
def start_vpn_server(server_id: int):
    server = VpnServer.objects.get(pk=server_id)
    try:
        server.vpn_service.do_vpn_server_start(server)
    except Exception as e:
        LOGGER.exception("Unable to start vpn server: {}".format(e))
        server.register_state_change_message(str(e))
        raise e
    server.register_state_change_message("Success")


@shared_task(name=const.JOB_ID_STOP_VPN_SERVER)
def stop_vpn_server(server_id: int):
    server = VpnServer.objects.get(pk=server_id)
    try:
        server.vpn_service.do_vpn_server_stop(server)
    except Exception as e:
        LOGGER.exception("Unable to stop vpn server: {}".format(e))
        server.register_state_change_message(str(e))
        raise e
    server.register_state_change_message("Success")


@shared_task(name=const.JOB_ID_RESTART_VPN_SERVER)
def restart_vpn_server(server_id: int):
    server = VpnServer.objects.get(pk=server_id)
    try:
        server.vpn_service.do_vpn_server_restart(server)
        server.register_state_change_message("Success")
    except Exception as e:
        LOGGER.exception("Unable to restart vpn server: {}".format(e))
        server.register_state_change_message(str(e))
        raise e
