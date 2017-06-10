import time
from picraftzero.log import logger
from pprint import pformat
import subprocess
import threading

from picraftzero.config import get_config


# see: https://pymotw.com/2/threading/




class RemoteCommands:

    DEFAULT_COMMAND_TIMEOUT_SECONDS = 30

    def __init__(self):
        self.user = 'pi'
        self.timeout = RemoteCommands.DEFAULT_COMMAND_TIMEOUT_SECONDS


    def run_remote_command(self, host, command, result):
        result[host]['COMMAND'] = command
        logger.debug("run_remote_command: {}".format([self.user, host, command]))
        prog = subprocess.Popen(["/usr/bin/ssh", "{}@{}".format(self.user, host), command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
        out = prog.communicate()
        result[host]['STATUS'] = 'COMPLETED'

        result[host]['RC'] = prog.returncode
        result[host]['STDOUT'] = out[0]
        result[host]['STDERR'] = out[1]

        #logger.error("stderr; {}".format(errdata))


    def run_remote_commands(self, hosts, command):
        results = {}
        threads = []

        for host in hosts:
            results[host] = {}
            results[host]['STATUS'] = 'STARTING'

            logger.debug("Host: {} Cmd: {}".format(host, command))
            t = threading.Thread(target=self.run_remote_command, args=(host, command, results), name=host)
            threads.append(t)
            t.start()

        for t in threads:
            logger.info('Waiting for %s', t.getName())
            t.join(self.timeout)
            logger.info('Final status for {} = {}'.format(t.getName(), t.isAlive()))

        logger.info("Results: {}".format(pformat(results)))
        for host in hosts:
            if host in results:
                if results[host]['STATUS'] != 'COMPLETED':
                    results[host]['STATUS'] = 'TIMEOUT'

                elif results[host]['RC'] == 0:
                    results[host]['STATUS'] = "OK"
                else:
                    results[host]['STATUS'] = "ERROR"
            else:
                logger.error("No results found for {}".format(host))

        return results

    def start_service(self, hosts, service):
        self.run_remote_commands(hosts, "sudo systemctl start {}".format(service))

    def restart_service(self, hosts, service):
        self.run_remote_commands(hosts, "sudo systemctl restart {}".format(service))

    def stop_service(self, hosts, service):
        self.run_remote_commands(hosts, "sudo systemctl stop {}".format(service))

    def disable_service(self, hosts, service):
        self.run_remote_commands(hosts, "sudo systemctl disable {}".format(service))

    def service_status(self, hosts, service):
        self.run_remote_commands(hosts, "sudo systemctl status {}".format(service))

    def reboot(self, hosts):
        self.run_remote_commands(hosts, "sudo reboot")

    def poweroff(self, hosts):
        self.run_remote_commands(hosts, "sudo poweroff")


    def _run_test(self, hosts, cmd):
        results = self.run_remote_commands(hosts, cmd)
        logger.info(pformat(results))



if __name__ == "TEST__main__":

    cmd = RemoteCommands()
    cmd._run_test(['cam0.local'], "sleep {}".format(cmd.timeout+10))
    cmd._run_test(['cam0.local'], "no_such_command")
    cmd._run_test(['no_such_host'], "date")
    cmd._run_test(['cam0.local'], "date")





# ----------------------------------------------------------------------------------------------


class PiCraftServices:

    def __init__(self):
        self.remote_cmds = RemoteCommands()
        self.config = get_config()
        self.camera_services = self.config['services_topology']['services']['camera']
        self.www_services = self.config['services_topology']['services']['www']
        self.topology = self.config['services_topology']['hosts_services_mapping']

    def all_hosts(self):
        return list(self.topology.keys())

    def all_services(self):
        all_services = []
        for host, services in self.topology.items():
            all_services += services
        return set(all_services)

    def hosts_for_service(self, service):
        hosts = []
        for host, services in self.topology.items():
            if service in services:
                hosts.append(host)
        logger.info("Service {} is installed on : {}".format(service, hosts))
        return hosts




    def camera_hosts(self):
        hosts = []
        for host, services in self.topology.items():
            #print(host, services)
            if set(self.camera_services).intersection(set(services)):
                hosts.append(host)
        return hosts


    def www_hosts(self):
        hosts = []
        for host, services in self.topology.items():
            if set(self.www_services).intersection(set(services)):
                hosts.append(host)
        return hosts

    # ---

    def service_status(self):
        for service in self.all_services():
            hosts = self.hosts_for_service(service)
            logger.info("Getting status for service {} on hosts: {}".format(service, hosts))
            self.remote_cmds.service_status(hosts, service)

    def www_services_status(self):
        for service in self.www_services:
            hosts = self.hosts_for_service(service)
            logger.info("Getting status for service {} on hosts: {}".format(service, hosts))
            self.remote_cmds.service_status(hosts, service)


    def camera_services_status(self):
        for service in self.camera_services:
            hosts = self.hosts_for_service(service)
            logger.info("Getting status for service {} on hosts: {}".format(service, hosts))
            self.remote_cmds.service_status(hosts, service)

    def restart_camera_services(self):
        for service in self.camera_services:
            self.remote_cmds.restart_service(self.camera_hosts(), service)

    def restart_www_services(self):
        for service in self.www_services:
            self.remote_cmds.restart_service(self.www_hosts(), service)

    def stop_www_services(self):
        for service in self.www_services:
            self.remote_cmds.stop_service(self.www_hosts(), service)


    def reboot_all(self):
        self.remote_cmds.reboot(self.all_hosts())

    def poweroff_all(self):
        self.remote_cmds.poweroff(self.all_hosts())
        #TODO: expected t fail!
""" 'cam2.local': {'COMMAND': 'sudo poweroff',
                'RC': 255,
                'STATUS': 'COMPLETED',
                'STDERR': 'Connection to cam2.local closed by remote host.\r\n',
                'STDOUT': ''}}"""






if __name__ == "__main__":
    # see: https://mkaz.tech/code/python-argparse-cookbook/
    import argparse

    pcs = PiCraftServices()

    logger.info("All hosts                 : {}".format(pcs.all_hosts()))
    logger.info("All services              : {}".format(pcs.all_services()))
    logger.info("Hosts with camera services: {}".format(pcs.camera_hosts()))
    logger.info("Hosts with www services   : {}".format(pcs.www_hosts()))

    commands = dict(
        service_status=pcs.service_status,
        www_service_restart=pcs.restart_www_services,
        www_service_status=pcs.www_services_status,
        www_service_stop=pcs.stop_www_services,
        camera_service_restart=pcs.restart_camera_services,
        camera_service_status=pcs.camera_services_status,
        reboot_all=pcs.reboot_all,
        poweroff_all=pcs.poweroff_all,
    )

    parser = argparse.ArgumentParser(description='Run admin scripts')

    parser.add_argument('-v', '--verbose', action="store_true", help="verbose output")
    parser.add_argument('-d', '--dryrun', action="store_true", help="dry run, don't execute remote commands")
    parser.add_argument('-l', '--logfile', type=argparse.FileType('w'), help="logfile to be created")
    parser.add_argument('-c', '--command', choices=list(commands.keys()), help="command")

    args = parser.parse_args()

    if args.command:
        commands[args.command]()
