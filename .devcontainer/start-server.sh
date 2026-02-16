#!/bin/bash
# Start the app server in a fully detached background process
(setsid python -m app.main > /tmp/app.log 2>&1 &)
exit 0
