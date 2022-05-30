![HidlRoute Cover Picture](https://raw.githubusercontent.com/HidlRoute/hidlroute-server/master/docs/assets/cover-picture.svg "HidlRoute Cover Picture")

<h1 align="center">Hidl Route</h1>
<p align="center">
<a href="https://pypi.org/project/hidlroute-server/"><img src="https://img.shields.io/pypi/l/hidlroute-server?style=for-the-badge" title="License: MIT"/></a> 
<a href="https://pypi.org/project/hidlroute-server/"><img src="https://img.shields.io/pypi/pyversions/hidlroute-server?style=for-the-badge" title="Python Versions"/></a> 
<a href="https://github.com/psf/black/"><img src="https://img.shields.io/badge/Code%20Style-black-black?style=for-the-badge" title="Code style: black"/></a>
<br>
<a href="https://github.com/hidlroute/hidlroute-server/actions/workflows/sanity-check.yml"><img src="https://img.shields.io/github/workflow/status/hidlroute/hidlroute-server/Sanity%20Check?style=for-the-badge" title="Build Status"/></a>
<a href="https://github.com/hidlroute/hidlroute-server/"><img src="https://img.shields.io/github/last-commit/hidlroute/hidlroute-server?style=for-the-badge" title="Last Commit"/></a> 
<a href="https://github.com/hidlroute/hidlroute-server/releases/"><img src="https://img.shields.io/github/release-date/hidlroute/hidlroute-server?style=for-the-badge" title="Last Release"/></a> 
</p>

Hidl Route (**hidl** - from the welsh filter) is an open-source VPN management system.

# Features

TBD

# Development environment

Ensure you have pre-requisites installed:

* Python 3.7+
* Make
* docker-compose

Run `make setup`. This will create Virtual Environment for project and install required dev. dependencies. Before making
any commit make use to run make to apply formatter, run linter and update copyright.

Run `make dev-containers` to launch related components e.g. redis, dev mail server etc.

# Credits

* Dmitry Berezovsky and Alex Cherednichenko, original authors

# Disclaimer

This module is licensed under GPLv3. This means you are free to use in non-commercial projects.

The GPL license clearly explains that there is no warranty for this free software. Please see the included LICENSE file
for details.
