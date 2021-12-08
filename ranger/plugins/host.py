"""
Make ranger as a host for neovim

"""
import os
import threading
import ranger
from .service import Service, ServiceRunner, ServiceLoader
from .rutil import attach_nvim


class Host():
    """
    Ranger host for RPC

    """

    def __init__(self, fm, hook_ready):
        self.fm = fm  # pylint: disable=invalid-name
        self.nvim = None
        self.old_hook_ready = hook_ready

    def host_ready(self):
        """
        Notify neovim that ranger host is ready

        """
        # job start with pty option in neovim only use stdout to communicate
        if os.getenv('RNVIMR_CHECKHEALTH'):
            print('RNVIMR_CHECKHEALTH', self.fm.host_id, 'RNVIMR_CHECKHEALTH')
        self.nvim.exec_lua('require("rnvimr.rpc").host_ready(...)', self.fm.host_id)

    def hook_ready(self):
        """
        Initialize host via ranger hook_ready.
        Manually redrawing UI can make users feel faster.

        """

        self.fm.ui.redraw()
        server_name = os.getenv('NVIM_LISTEN_ADDRESS')
        self.nvim = attach_nvim(server_name)
        if self.nvim:
            self.fm.service = Service()
            # call neovim only once as a host in order to get channel id.
            self.fm.host_id = self.nvim.request('nvim_get_api_info')[0]

            t_run_loop = threading.Thread(
                daemon=True, target=self.nvim.run_loop,
                args=(self.request_event, self.notify_event))
            t_run_loop.start()

            self.nvim.async_call(self.host_ready)

        return self.old_hook_ready(self.fm)

    def notify_event(self, method, args):  # pylint: disable=no-self-use
        """
        notify event called by pynvim

        :param method str: method name of service
        :param args list: list of arguments
        """
        ServiceLoader('notifying method: {}.'.format(method), method, args).load()

    def request_event(self, method, args):  # pylint: disable=no-self-use
        """
        request event called by neovim

        :param method str: method name of service
        :param args list: list of arguments
        """
        return ServiceRunner(method, args).run()


OLD_HOOK_READY = ranger.api.hook_ready
ranger.api.hook_ready = lambda fm: Host(fm, OLD_HOOK_READY).hook_ready()
