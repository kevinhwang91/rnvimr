"""
Build the service of ranger

"""
from ranger.core.loader import Loadable
from ranger.core.shared import FileManagerAware


class Service(FileManagerAware):
    """
    Service called by neovim

    """

    class Register():
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
            return
        Service.Register.table[method](self, args)

    @Register
    def attach_file(self, args):
        """
        Select file

        :param args list: The last element is target path
        """
        try:
            path = args[-1]
        except IndexError:
            return
        else:
            self.fm.execute_console('AttachFile {}'.format(path))


class ServiceLoader(Loadable, FileManagerAware):
    """
    Execute the service in a loader of ranger
    
    """

    def __init__(self, descr, event, args):
        Loadable.__init__(self, self.generate(), descr)
        self.event = event
        self.args = args

    def generate(self):
        """
        Generator of ranger loader

        """
        self.fm.service.call(self.event, self.args)
        yield
