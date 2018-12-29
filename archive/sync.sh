# Only works when SSH is configured correctly
# The sync is one-way - data from the server is pulled locally, not the other
# way around.
rsync -azP worship:~/.worship-manager/data ~/.worship-manager/.
