"""
This fabfile contains recipes for deploying and starting lastpage.me
"""
from __future__ import with_statement
from fabric.api import require, run, local, env, put, cd, settings
from datetime import datetime


def live():
    """
    Define the live host.
    """
    RELEASE = datetime.utcnow().strftime('%Y%m%d-%H%M%S')
    env.hosts = ['lastpage@lastpage.me']
    env.sitename = 'lastpage'
    # from subprocess import Popen, PIPE
    # revno = Popen(['bzr', 'revno'], stdout=PIPE).communicate()[0][:-1]
    # env.tag = '%s-r%s-%s' % (env.sitename, revno, RELEASE)
    env.tag = '%s-%s' % (env.sitename, RELEASE)


def upload():
    """
    Upload deployment files to the server. Note that $HOME for the lastpage
    user on lastpage.me is /srv/lastpage, so all calls to put() have that
    as their cwd.
    """
    require('hosts', provided_by=[live])

    # Bundle, upload, and extract lastpage-server.
    local('cd ../lastpage-server && '
          'git archive --prefix=%(tag)s/ -v --format tar HEAD | '
          'bzip2 > %(tag)s-server.tar.bz2' % env)
    put('../lastpage-server/%(tag)s-server.tar.bz2' % env, '.')
    run('tar xjvf %(tag)s-server.tar.bz2' % env)

    # Bundle, upload, and extract lastpage-deploy into the same place.
    local('git archive --prefix=%(tag)s/ -v --format tar HEAD | '
          'bzip2 > %(tag)s-deploy.tar.bz2' % env)
    put('%(tag)s-deploy.tar.bz2' % env, '.')
    run('tar xjvf %(tag)s-deploy.tar.bz2' % env)

    # Create a virtualenv for the new distribution.
    run('virtualenv --no-site-packages %(tag)s' % env)

    # Install requirements.
    run('%(tag)s/bin/pip install --upgrade -r %(tag)s/requirements.txt' % env)

    # Make var/{run,log} dirs for runtime files. Touch the log so its perms
    # get set correctly.
    run('mkdir -p %(tag)s/var/run' % env)
    run('mkdir -p %(tag)s/var/log' % env)
    run('touch %(tag)s/var/log/lastpage.log' % env)

    # Allow other users to see the files/dirs on the remote server.
    run('find %(tag)s -type f -print0 | xargs -0 chmod go+r' % env)
    run('find %(tag)s -type d -print0 | xargs -0 chmod go+rx' % env)


def stop_server():
    """
    Stop any currently running lastpage server.
    """
    require('hosts', provided_by=[live])

    print('Stopping lastpage server....')
    with settings(warn_only=True):
        result = run('cat current/var/run/lastpage.pid | xargs kill')
        if result.failed:
            print 'No lastpage server was running.'


def _start_server():
    """
    Link the newly uploaded deployment in the right place in the filesystem
    and start the Twisted Lastpage server.  Note that you cannot run this
    command by itself, since 'tag' has to be set to an already uploaded
    distribution.
    """
    require('hosts', provided_by=[live])
    run('rm -f current')
    run('ln -s %(tag)s current' % env)
    with cd('current'):
        # For now we're starting Lastpage via a shell script. This will be
        # changed to use upstart.
        # run('restart %(sitename)s' % env)
        run('bin/run-lastpage.sh')


def deploy():
    """
    Wraps all the steps up to deploy to the live server.
    """
    upload()
    stop_server()
    _start_server()
