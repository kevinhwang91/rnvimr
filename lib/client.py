"""
A client of neovim.
"""
import os
import pynvim

SOCKET_PATH = os.getenv('NVIM_LISTEN_ADDRESS')

if SOCKET_PATH:
    client = pynvim.attach('socket', path=SOCKET_PATH) # pylint: disable=invalid-name
