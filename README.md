# OpenVPN-Servers-Configuration-files-Downloader

OpenVPN-Servers-Configuration-files-Downloader is a small python program which retrieves vpn servers data from www.vpngate.net and extract openvpn configuration files from the data.

hosts_manager creates .ovpn files inside 'ovpn files/' directory numbered from 1 to 10 based on quality, servers speed, number of sessions and ping response time

you can add hosts_manager.py to your startup programs and have vpn servers updated every hour which can then be used with OpenVPN softwares

Added the feature of blocking outside dns for better security

it is supported for both linux and windows platforms
