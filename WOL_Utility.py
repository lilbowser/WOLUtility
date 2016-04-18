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
    import os
    import platform

    giveFeedback = False

    if platform.system() == "Windows":
        response = os.system("ping " + hostname + " -n 1")
    else:
        response = os.system("ping -c 1 " + hostname)

    isUpBool = False
    if response == 0:
        if giveFeedback:
            print(hostname + 'is up!')
        isUpBool = True
    else:
        if giveFeedback:
            print(hostname + 'is down!')

    return isUpBool


if __name__ == '__main__':
    import time
    config = load_config()
    testDict = {'a': 'one', 'b': 'two'}
    print("Please enter one of the following hostnames to send a magic packet")
    for hostname, mac_address in config['hostnames'].items():
        print(hostname)
    # selected_hostname = input("")
    selected_hostname = "rainbowdash"
    try:
        selected_mac = config['hostnames'][selected_hostname]
    except KeyError as e:
        print("Invalid hostname")
        input("Press enter to exit")
        sys.exit(1)
    wake_on_lan(selected_mac)
    print("Magic packet has been sent to {}. Please wait at least 60 seconds for machine to respond.".format(selected_hostname))

    # start_time = time.time()
    # while True:
    #     time.sleep(5)
    #     elapsed_time = time.time() - start_time
    #     if check_host_status(selected_hostname):
    #         print("Host is now up after {:5f} seconds!".format(elapsed_time))
    #         time.sleep(10)
    #         sys.exit(0)
    #     else:
    #         print("{:5f} seconds have elapsed sense sending the magic packet".format(elapsed_time))
    #         if elapsed_time > 120:
    #             print("Magic Packet has timed out.")
    #             time.sleep(10)
    #             sys.exit(1)