
import hupper
from cleo import Command


class ServeCommand(Command):
    """
    Run the Masonite server

    serve
        {--port=8000 : Specify which port to run the server}
        {--host=127.0.0.1 : Specify which ip address to run the server}
        {--r|reload : Make the server automatically reload on file changes}
    """

    def handle(self):
        # Check for the 2.0 patch.
        self._check_patch()

        if self.option('reload'):
            logger = hupper.DefaultLogger(1)

            # worker args are pickled and then passed to the new process
            worker_args = [
                self.option("host"), self.option("port"), "wsgi:application",
            ]

            reloader = hupper.Reloader(
                "masonite.commands._devserver.run",
                hupper.find_default_monitor_factory(logger),
                logger,
                worker_args=worker_args,
            )

            # monitor the env file too
            reloader.watch_files(['.env'])

            # Run the reloader
            reloader.run()

        else:
            from wsgi import application
            from ._devserver import run
            run(self.option("host"), self.option("port"), application)

    def _check_patch(self):
        patched = False

        with open('wsgi.py', 'r') as file:
            # read a list of lines into data
            data = file.readlines()

        # change the line that starts with KEY=
        for line_number, line in enumerate(data):
            if line.startswith("for provider in container.make('Providers'):"):
                patched = True
                break

        if not patched:
            print('\033[93mWARNING: {}\033[0m'.format(
                "Your application does not have a 2.0 patch! You can read more about this patch here: https://dev.to/josephmancuso/masonite-framework-20-patch-3op2"))
