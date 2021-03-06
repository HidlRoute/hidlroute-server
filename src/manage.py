#!/usr/bin/env python

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

"""Django's command-line utility for administrative tasks."""
import os
import sys

try:
    if os.environ.get("REMOTE_DEBUG", "0").lower() in ["yes", "true", "1"]:
        import pydevd_pycharm

        pydevd_pycharm.settrace('localhost', port=int(os.environ.get("REMOTE_DEBUG_PORT", "9543")),
                                stdoutToServer=True, stderrToServer=True)
except ImportError:
    pass

if __name__ == '__main__':
    from hidlroute import cli as hidlroute_cli

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hidlroute.settings.dev')
    hidlroute_cli.entrypoint()
