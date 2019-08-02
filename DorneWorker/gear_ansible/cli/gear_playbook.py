# -*- coding: utf-8 -*-

from ansible.cli import CLI
from ansible.cli.playbook import PlaybookCLI
from ansible.errors import AnsibleOptionsError

try:
    from __main__ import display
except ImportError:
    from ansible.utils.display import Display
    display = Display()


class GearPlayBookCLI(PlaybookCLI):
    """playbook cli with job_id and callback server options"""

    def parse(self):
        parser = CLI.base_parser(
            usage="%prog [options] playbook.yml [playbook2 ...]",
            connect_opts=True,
            meta_opts=True,
            runas_opts=True,
            subset_opts=True,
            check_opts=True,
            inventory_opts=True,
            runtask_opts=True,
            vault_opts=True,
            fork_opts=True,
            module_opts=True,
            desc="Runs Ansible playbooks, executing the defined tasks on the targeted hosts.",
        )

        # ansible playbook specific opts
        parser.add_option('--list-tasks', dest='listtasks', action='store_true',
                          help="list all tasks that would be executed")
        parser.add_option('--list-tags', dest='listtags', action='store_true',
                          help="list all available tags")
        parser.add_option('--step', dest='step', action='store_true',
                          help="one-step-at-a-time: confirm each task before running")
        parser.add_option('--start-at-task', dest='start_at_task',
                          help="start the playbook at the task matching this name")

        # gear playbook specific opts
        parser.add_option('--callback-url', dest='callback_url', type='string', default='/',
                          help="set a callback url. default is '/'")

        self.parser = parser
        super(PlaybookCLI, self).parse()

        if len(self.args) == 0:
            raise AnsibleOptionsError("You must specify a playbook file to run")

        display.verbosity = self.options.verbosity
        self.validate_conflicts(runas_opts=True, vault_opts=True,
                                fork_opts=True)
