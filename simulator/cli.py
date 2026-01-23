# This file will serve as the command-line tool to run the cargo simulation.
#"python simulator.py --nodes 5 --duration 60" - example command

# Accepted arguments will be -nodes (how many packages),
# -duration (how long each node lives for),
# and -rate.

# Make sure we are constantly printing status updates to know what's
# happening with the nodes. Also, make sure we are handling ctrl-c the same way it would in a normal command line setting.

# We are done one we can run and publish multiple nodes to REDIS for some set duration of time