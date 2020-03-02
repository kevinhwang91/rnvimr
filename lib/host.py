"""
Make ranger as a host for neovim
"""
import os
import threading
import pynvim
import ranger
from .service import Service, ServiceLoader


class Host():
    """
    Ranger host for RPC
    """

    def __init__(self, fm, hook_ready):
        self.fm = fm  # pylint: disable=invalid-name
        self.old_hook_ready = hook_ready
        self.chan_id = -1
        self.service = None

    def hook_ready(self):
        """Initialize host via ranger hook_ready."""

        socket_path = os.getenv('NVIM_LISTEN_ADDRESS')

        if socket_path:
            host = pynvim.attach('socket', path=socket_path)
            self.fm.service = Service()

            # call neovim only once as a host in order to get channel id.
            self.chan_id = host.request('nvim_get_api_info')[0]
            host.call('rnvimr#rpc#set_host_chan_id', self.chan_id)

            t_run_loop = threading.Thread(
                daemon=True, target=host.run_loop,
                args=(self.request_event, self.notify_event))
            t_run_loop.start()

        return self.old_hook_ready(self.fm)

    def notify_event(self, method, args):
        """
        notify event called by pynvim

        :param method str: method name of service
        :param args list: list of arguments
        """
        loadable = ServiceLoader(
            'notifying method: {}.'.format(method), method, args)
        self.fm.loader.add(loadable, append=True)

    def request_event(self, method, args):
        """
        request event called by neovim

        :param method str: method name of service
        :param args list: list of arguments
        """
        # reserve the request event for further extension


OLD_HOOK_READY = ranger.api.hook_ready
ranger.api.hook_ready = lambda fm: Host(fm, OLD_HOOK_READY).hook_ready()
