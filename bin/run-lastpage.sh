#!/bin/sh

# This is a script that can start lastpage.

test -d /srv/lastpage || {
  cat 2>&1 <<EOF

This script is designed to run only on lastpage.me (which has a
/srv/lastpage directory - that you don't have). To start lastpage locally,
go to the top level of your tree, and use:

  $ make
  $ make run
EOF
  exit 1
}

VIRTUALENV_HOME=/srv/lastpage/current
LASTPAGE_USER=lastpage

exec /sbin/start-stop-daemon --start --chdir $VIRTUALENV_HOME \
    --chuid $LASTPAGE_USER --exec $VIRTUALENV_HOME/bin/twistd -- \
    --pidfile=/srv/lastpage/current/var/run/lastpage.pid \
    --logfile=/srv/lastpage/current/var/log/lastpage.log \
    lastpage \
    --port 11111
