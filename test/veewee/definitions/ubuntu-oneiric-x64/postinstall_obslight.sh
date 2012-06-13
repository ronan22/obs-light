#
# OBS Light post-installation configuration
#
# http://en.opensuse.org/openSUSE:OBS_Light_Installation#For_Ubuntu
#

# Add vagrant to "users" group
usermod -a -G users vagrant

# Add packages repositories for OBS Light
cat > /etc/apt/sources.list.d/obslight.list << EOF
# Ubuntu 11.10
## MIC and dependencies
deb http://download.meego.com/live/devel:/tools:/building/xUbuntu_11.10/ ./
## OBS Light
deb http://repo.pub.meego.com/Project:/OBS_Light/Ubuntu_11.10/ ./
EOF
apt-add-repository ppa:pyside/ppa

# Refresh package database
apt-get -y update

# Download OBS Light and its dependencies, without installing them
apt-get -y --allow-unauthenticated -d install obslight

