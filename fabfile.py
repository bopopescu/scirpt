from fabric.api import run,abort,env,settings
from fabric.colors import *
from fabric.contrib.console import confirm

env.hosts = ['10.2.0.20','10.2.0.21','10.2.0.22','10.2.0.23','10.2.0.24','10.2.0.25']
env.user = 'root'
env.password = 'password'
path_config = r"/etc/salt/minion"
def install_salt():
        with settings(warn_only=True):
                result=run('apt-get install salt-minion -y')
        if result.failed:
                abort(red("install salt-minion fail!!"))
        else:
                print(green("install salt-minion success"))
def config_salt():
#        result = run("sed -i 's/^#master:.*/master: 10.1.0.12/' %s" % path_config)
#        if result.failed:
#                abort(red("modifiy minion failed!!"))
#        else:
        run("service salt-minion restart")
        print(green("modifiy minion success"))
def main():
#        install_salt()
        config_salt()
