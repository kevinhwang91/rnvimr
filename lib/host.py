"""
Make ranger as a host.
"""
import os
import threading
import pynvim
import ranger
from ranger.core.loader import Loadable
from ranger.core.shared import FileManagerAware


class Host():
    """
    Ranger host for RPC, will refactor this file as soon as possible.
    """

    def __init__(self, fm, hook_ready):
        self.fm = fm  # pylint: disable=invalid-name
        self.old_hook_ready = hook_ready
        self.chan_id = -1

    def hook_ready(self):
        """Initialize host via ranger hook_ready."""

        socket_path = os.getenv('NVIM_LISTEN_ADDRESS')

        if socket_path:
            host = pynvim.attach('socket', path=socket_path)

            # call neovim only once as a host in order to get channel id.
            self.chan_id = host.request('nvim_get_api_info')[0]
            host.call('rnvimr#rpc#set_host_chan_id', self.chan_id)

            t_run_loop = threading.Thread(
                daemon=True, target=host.run_loop,
                args=(self.request_event, self.notify_event))
            t_run_loop.start()

        return self.old_hook_ready(self.fm)

    def notify_event(self, method, args):
        loadable = NvimLoader('notifying method: {}.'.format(method), method, args)
        self.fm.loader.add(loadable, append=True)

    def request_event(self, method, args):
        # TODO: reserve the request event
        pass


class NvimLoader(Loadable, FileManagerAware):

    def __init__(self, descr, event, args):
        Loadable.__init__(self, self.generate(), descr)
        self.event = event
        self.args = args

    #  TODO harcode event, please refactor it for further extensions
    def generate(self):
        if self.event == 'select_file':
            try:
                self.fm.select_file(self.args[-1])
            except IndexError:
                return
            # Redraw statusbar cause by generator of Dictionary
            loadable = NvimLoader('Redraw manually after select_file event', 'redraw', None)
            self.fm.loader.add(loadable, append=True)
        if self.event == 'enter_dir':
            try:
                self.fm.enter_dir(self.args[-1])
            except IndexError:
                return
        if self.event == 'redraw':
            self.fm.ui.status.request_redraw()
        yield


OLD_HOOK_READY = ranger.api.hook_ready
ranger.api.hook_ready = lambda fm: Host(fm, OLD_HOOK_READY).hook_ready()
