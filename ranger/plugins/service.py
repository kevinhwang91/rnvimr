"""
Build the service of ranger

"""
from ranger.core.loader import Loadable
from ranger.core.shared import FileManagerAware


class Service(FileManagerAware):
    """
    Service called by neovim

    """

    class Register():  # pylint: disable=too-few-public-methods
        """
        Using a class to decorate the service to register the service into table

        """
        table = {}

        def __new__(cls, method):
            cls.table[method.__name__] = method
            return method

    def call(self, method, args):
        """
        Call service by method name

        :param method str: method name of registered service
        :param args list: list of arguments
        """
        if method not in Service.Register.table:
            return '{} did not register in table'.format(method)
        return Service.Register.table[method](self, args)

    @Register
    def attach_file(self, args):
        """
        Select file

        :param args list: The last element is target path
        """
        try:
            line = args[0]
            path = args[1]
        except IndexError:
            return
        else:
            self.fm.execute_console('AttachFile {} {}'.format(line, path))

    @Register
    def eval_cmd(self, args):
        """
        Eval ranger command

        :param args list: list of commands
        """
        cmd = args[0]

        if not cmd:
            self.fm.client.echom('eval empty command')

        try:
            self.fm.execute_console(' '.join(cmd))
        except Exception as ex:  # pylint: disable=broad-except
            self.fm.client.echom(ex)

    @Register
    def clear_image(self, args):  # pylint: disable=unused-argument
        """
        Clear Image

        :param args args list: No use
        """
        self.fm.execute_console('ClearImage')

    @Register
    def destroy(self, args):  # pylint: disable=unused-argument
        """
        Destroy everything execpt heavy UI

        :param args args list: No use
        """
        self.fm.ui.console.destroy()
        self.fm.loader.destroy()

    @Register
    def echo(self, args):  # pylint: disable=no-self-use
        """
        Echo Test for checkhealth

        :param args list: List of string
        """

        return ''.join(args)


class ServiceRunner(FileManagerAware):
    """
    Service runner instance

    """

    def __init__(self, event, args):
        self.event = event
        self.args = args

    def run(self):
        """
        Run the registered services

        """
        return self.fm.service.call(self.event, self.args)


class ServiceLoader(Loadable, ServiceRunner):
    """
    Service in a loader instance of ranger

    """

    def __init__(self, descr, event, args):
        Loadable.__init__(self, self.generate(), descr)
        ServiceRunner.__init__(self, event, args)

    def generate(self):
        """
        Generator for wrapping ServiceRunner.run()

        """
        yield self.run()

    def load(self):
        """
        Add the loader to ranger

        """
        self.fm.loader.add(self, append=True)
