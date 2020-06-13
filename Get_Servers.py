#!/usr/bin/env python3

# Get_Servers.py is a small script which retrieves vpn servers data from vpngate.net
# and extract openvpn configuration files from the data.
# All rights reserved to Mohammed Abdelmonem, mohammedhll222@gmail.com

import urllib.request, csv, sys, base64
from os import path, getcwd, chdir
import platform
import pathlib

plt = platform.system()
hosts_filename = '.servers.csv' if plt == 'Linux' else 'servers.csv'

VPN_SERVERS_ADDRESS = 'http://www.vpngate.net/api/iphone/'
SERVERS_COUNT = 10
CWD = path.dirname(path.realpath(__file__))
pathlib.Path(path.join(CWD, 'ovpn files')).mkdir(exist_ok=True)


def to_int(s):
    try:
        return int(s)
    except Exception:
        return 0


def s_key(row):  # sorts the servers
    speed = to_int(row['Speed'])
    sessions = to_int(row['NumVpnSessions'])
    ping = to_int(row['Ping'])
    quality = to_int(row['Score'])
    return ((speed * quality) ** 2 * sessions)


def update_servers():  # if the user passes '--update' via the commandline, this function would pull the latest servers data
    try:
        servers_csv = urllib.request.urlopen(VPN_SERVERS_ADDRESS).read().decode().split('\n')[1:]
        with open(path.join(CWD, hosts_filename), 'w') as cash_file:
            print('updating servers...')
            for row in servers_csv:
                cash_file.write(row)
    except Exception as e:
        print(e)


def load_hosts(hosts_csv, excluded=None):
    if excluded is None: excluded = []
    with open(hosts_csv, 'r') as cash_file:
        reader = csv.DictReader(cash_file)
        rows = [row for row in reader if not row['CountryLong'] in excluded]
        rows.sort(key=s_key, reverse=True)
    return rows


def create_ovpn_files(servers_count, hosts=None, management_sock_name=None):
    print('creating ovpn files...')
    logg = open(path.join(CWD, 'log.txt'), 'w')
    # due to connection problems arising between most vpn servers located in these two regions and my own ISP, i filtered them out
    if hosts == None:
        hosts = load_hosts(path.join(CWD, hosts_filename))  # excluded= ['United States', 'United Kingdom']

    for count, row in enumerate(hosts):
        if count + 1 > servers_count:
            break

        # print and log basic info of the ovpn file
        print(
            f"server {count + 1}: Speed {round(to_int(row['Speed']) / 1024 ** 2)} Mb/s  sessions {row['NumVpnSessions']}  location  {row['CountryLong']} ping {row['Ping']} ms")
        logg.write(
            f"server {count + 1}: Speed {round(to_int(row['Speed']) / 1024 ** 2)} Mb/s  sessions {row['NumVpnSessions']}  location  {row['CountryLong']} ping {row['Ping']} ms\n")

        # create and write downloaded info to a .ovpn file
        with open(path.join(CWD, f'ovpn files/{count + 1}.ovpn'), 'w') as ovpn_file:
            ovpn_file.write("###############################################################################\n")
            ovpn_file.write(f"# Host Name : {row['#HostName']}\n")
            ovpn_file.write(f"# IP Address : {row['IP']}\n")
            ovpn_file.write(f"# Country : {row['CountryLong']}\n")
            if row['Message'] != '':
                ovpn_file.write(f"# Message : {row['Message']}\n")
                logg.write(f"# Message : {row['Message']}\n")

            # Configuration files are Base64 encoded
            ovpn_file.write('\n')
            ovpn_file.write(base64.b64decode(row['OpenVPN_ConfigData_Base64']).decode('utf-8'))

            # if you want to control OpenVPN via sockets set management_sock_name = (ipaddress, port)
            if management_sock_name != None:
                ovpn_file.write(f'\nmanagement {management_sock_name[0]} {management_sock_name[1]}\n')

            # This bit of code aims to address dns leak issues
            if plt == 'Linux':
                ovpn_file.write(
                    '\nscript-security 2\nup /etc/openvpn/update-resolv-conf\ndown /etc/openvpn/update-resolv-conf')
            elif plt == 'Windows':
                ovpn_file.write('\n--block-outside-dns')

    print('Completed successfully!')
    logg.close()


def main():
    global SERVERS_COUNT
    if '--update' in sys.argv:
        update_servers()

    # specifies how many openvpn configuration files to create
    if '--count' in sys.argv:
        index = sys.argv.index('--count') + 1
        if index < len(sys.argv):
            num = to_int(sys.argv[index])
            SERVERS_COUNT = num if num != 0 else SERVERS_COUNT

    create_ovpn_files(SERVERS_COUNT)


if __name__ == '__main__':
    main()
