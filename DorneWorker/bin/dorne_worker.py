#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gearman
import sys
import requests
import json
import signal
import subprocess
from argparse import ArgumentParser
from gear_ansible.report import Report


class JobArgumentsError(Exception):
    def __init__(self, message=None):
        super(JobArgumentsError, self).__init__()
        self.message = message


def report_error_msg(callback_url, msg):
    """"""
    try:
        r = requests.post(callback_url, data=msg, timeout=(4, 15))
        r.raise_for_status()

        # TODO: log error
    except requests.exceptions.Timeout:
        pass
    except requests.exceptions.HTTPError:
        pass
    except requests.exceptions.ConnectionError:
        pass


def run(inventory_file, playbook_file, callback_url, others=None):
    """
    """
    cli_args = [
        'ansible-playbook',
        '-i',
        inventory_file,
    ]

    if others is not None:
        evars = others.get('extra_variables')
        limit = others.get('limit')
        forks = others.get('forks')
        tags = others.get('job_tags')
        verbose = int(others.get('verbosity', 0))
        check = others.get('check', False)
        connection = others.get('connection')

        if evars:
            cli_args.append('-e')
            cli_args.append("\'%s\'" % json.dumps(evars))
        if limit:
            cli_args.append('-l')
            cli_args.append(limit)
        if connection:
            cli_args.append('-c')
            cli_args.append(connection)
        if forks:
            cli_args.append('-f')
            cli_args.append(forks)
        if tags:
            cli_args.append('-t')
            cli_args.append(tags)
        if check:
            cli_args.append('-C')
        if verbose:
            vb = ['-', ]
            for v in range(0, verbose):
                vb.append('v')

            cli_args.append(''.join(vb))

    cli_args.append(playbook_file)
    cmd = " ".join(cli_args)
    return subprocess.check_output(cmd, shell=True)


def run_playbook(worker, job):
    """run a playbook"""
    job_data = json.loads(job.data)
    inventory_file = job_data.get('inventory_file', None)
    playbook_file = job_data.get('playbook_file', None)
    callback_url = job_data.get('callback_url', None)
    others = job_data.get('args', dict())
    reporter = Report(callback_url)
    try:
        output = run(inventory_file, playbook_file, callback_url, others)
        reporter.report(output)

    # TODO: log error message into file
    # exit code not 0
    except subprocess.CalledProcessError as e:
        err_info = "exit_code: %s cmd: %s msg: %s" % (e.returncode, e.cmd,
                                                      e.output)
        msg = dict(error=err_info)
        reporter.report(msg, 1)

    finally:
        return "1"


def signal_handler(sig, frame):
    """"""
    gm_worker.unregister_task('run_playbook')
    # TODO: log message
    sys.exit(0)


if __name__ == "__main__":

    parser = ArgumentParser(usage="dorne_worker [options] functions")
    parser.add_argument('-s', '--servers', type=str, required=True,
                        action='append', dest='servers', help='gearmand servers')
    parser.add_argument('-p', '--port', type=str, default='4730',action='store',
                        dest='port',help='gearmand server port')
    parser.add_argument('-i', '--worker-id', type=str, dest='id', required=True,
                        action='store', help='gearmand worker id')

    args = parser.parse_args()
    options = vars(args)

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGHUP, signal_handler)

    gm_worker = None
    try:
        gm_worker = gearman.GearmanWorker(
            ["%s:%s" % (host, options['port']) for host in options['servers']]
        )
        gm_worker.set_client_id(options['id'])
        gm_worker.register_task('run_playbook', run_playbook)
        gm_worker.work()

    except KeyboardInterrupt:
        gm_worker.unregister_task('run_playbook')
        sys.exit(0)

    except Exception as e:
        # TODO: log error message into file
        print "unknow error: %s" % e.message
        sys.exit(1)
