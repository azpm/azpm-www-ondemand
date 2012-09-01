from __future__ import with_statement
from fabric.api import settings, run, cd

def deploy():
    code_dir = '/srv/vhosts/ondemand/'
    with settings(warn_only=True):
        if run("test -d %s" % code_dir).failed:
            run("git clone git@github.com:azpm/azpm-www-ondemand.git %s" % code_dir)
            run("setfacl -m d:g:http_srv:rwx %slogs")

    with cd(code_dir):
        run("git pull")

    load_config()

def restart_site():
    working_dir = '/srv/vhosts/ondemand/public'
    with cd(working_dir):
        run("touch run.wsgi")

def load_config(mode="production"):
    working_dir = '/srv/vhosts/'
    with cd(working_dir):
        run("cp deployment/{0:>s}/ondemand/local_settings.py ondemand/project/".format(mode))