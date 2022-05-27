import sys

from celery import shared_task

from hidlroute.vpn import const
from hidlroute.vpn.models import VpnServer


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
        server.register_state_change_message(str(e))
        raise e
    server.register_state_change_message("Success")


@shared_task(name=const.JOB_ID_STOP_VPN_SERVER)
def stop_vpn_server(server_id: int):
    server = VpnServer.objects.get(pk=server_id)
    try:
        server.vpn_service.do_vpn_server_stop(server)
    except Exception as e:
        server.register_state_change_message(str(e))
        raise e
    server.register_state_change_message("Success")


@shared_task(name=const.JOB_ID_RESTART_VPN_SERVER)
def restart_vpn_server(server_id: int):
    server = VpnServer.objects.get(pk=server_id)
    try:
        server.vpn_service.restart(server)
        server.register_state_change_message("Success")
    except Exception as e:
        server.register_state_change_message(str(e))
        raise e
