#! python3
"""
WOL Utility.
Created April 2016
"""

import socket
import sys
import struct
import logging

log = logging.getLogger("WOL")
def wake_on_lan(macaddress):
    """
    Switches on remote computers using WOL.

    @param macaddress: The mac address of the host you wish to wake up.
    Format: xxxxxxxxxxxx, xx-xx-xx-xx-xx-xx, xx xx xx xx xx xx, ect
    @type macaddress: str

    """

    # Check macaddress format and try to compensate.
    if len(macaddress) == 12:
        pass
    elif len(macaddress) == 12 + 5:
        sep = macaddress[2]
        macaddress = macaddress.replace(sep, '')
    else:
        raise ValueError('Incorrect MAC address format')

    # Pad the synchronization stream.
    # data = ''.join(['FFFFFFFFFFFF', macaddress * 20])
    # send_data = ''
    data = b'FFFFFFFFFFFF' + (macaddress * 20).encode()
    send_data = b''

    # Split up the hex values and pack.
    for i in range(0, len(data), 2):
        # send_data = ''.join([send_data,
        #                      struct.pack('B', int(data[i: i + 2], 16))])
        send_data += struct.pack('B', int(data[i: i+2], 16))

    # Broadcast it to the LAN.
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(send_data, ("<broadcast>", 7))
    return True


def load_config(URI="config.yaml"):
    import yaml

    with open(URI, 'r') as stream:
        try:
            _config = yaml.load(stream)
        except yaml.YAMLError as e:
            log.exception()

    return _config

def check_host_status(hostname):
    """
    On a successful reply, we will see:
    Packets: Sent = 1, Received = 1, Lost = 0 (0% loss),
    Check for that, instead of return code.
    :param hostname:
    :return:
    """

    import subprocess as sp
    import sys

    try:
        output = sp.check_output(["ping", hostname, '-n', '1'])

    except sp.CalledProcessError as e:
        output = None
        return False

    str_out = output.decode(sys.stdout.encoding)
    if "Packets: Sent = 1, Received = 1, Lost = 0 (0% loss)," in str_out and \
            "Approximate round trip times in milli-seconds:" in str_out:
        return True
    else:
        return False

if __name__ == '__main__':
    import time
    import argparse

    # Set up argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--mac', help='Send magic packet to mac address.')
    parser.add_argument('--host', help='Send magic packet to hostname or IP address (Host must be in config file).')
    args = parser.parse_args()


    # Load Configureation data
    config = load_config()
    selected_mac = None
    if args.mac is not None:
        selected_mac = args.mac
        selected_hostname = args.mac
    else:
        if args.host is not None:
            selected_hostname = args.host
        else:
            print("Please enter one of the following hostnames to send a magic packet")
            for hostname, mac_address in config['hostnames'].items():
                print(hostname)
            selected_hostname = input("")
            # selected_hostname = "rainbowdash"
        try:
            selected_mac = config['hostnames'][selected_hostname]
        except KeyError as e:
            print("Invalid hostname")
            input("Press enter to exit")
            sys.exit(1)

    wake_on_lan(selected_mac)
    print("Magic packet has been sent to {}. Please wait for machine to respond.".format(selected_hostname))
    # input("Press enter to exit")
    # sys.exit(0)

    start_time = time.time()
    while True:
        time.sleep(5)
        elapsed_time = time.time() - start_time
        if check_host_status(selected_hostname):
            print("Host is now up after {:.0f} seconds!".format(elapsed_time))
            time.sleep(10)
            sys.exit(0)
        else:
            print("{:.0f} seconds have elapsed sense sending the magic packet".format(elapsed_time))
            if elapsed_time > 120:
                print("Magic Packet has timed out after 120 seconds.")
                time.sleep(10)
                sys.exit(1)
