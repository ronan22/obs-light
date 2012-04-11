#
# OBS Light post-installation configuration
#
# http://wiki.meego.com/OBS_Light_Installation#For_OpenSUSE_12.1
#

# Add vagrant to "users" group
usermod -a -G users vagrant

# Add packages repositories for OBS Light
zypper ar -f http://download.meego.com/live/devel:/tools:/building/openSUSE12.1/ tizen_tools
zypper ar -f http://repo.pub.meego.com/Project:/OBS_Light/openSUSE_12.1/Project:OBS_Light.repo

# Disable GPG checks
echo "gpgcheck=0" | tee -a "/etc/zypp/repos.d/Project_OBS_Light.repo" > /dev/null
echo "gpgcheck=0" | tee -a "/etc/zypp/repos.d/tizen_tools.repo" > /dev/null

# Refresh package database
zypper --non-interactive --gpg-auto-import-keys ref

# Download OBS Light and its dependencies, without installing them
zypper --non-interactive install --download-only obslight

