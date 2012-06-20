#
# OBS Light post-installation configuration
#
# http://en.opensuse.org/openSUSE:OBS_Light_Installation#For_Fedora_16
#

# Add vagrant to "users" group
usermod -a -G users vagrant

# Add packages repositories for OBS Light
wget http://repo.pub.meego.com/Project:/OBS_Light/Fedora_16/Project:OBS_Light.repo -O /etc/yum.repos.d/Project_OBS_Light.repo

# Disable GPG checks
sed -r -i "s/(gpgcheck)=1/\1=0/" /etc/yum.repos.d/Project_OBS_Light.repo

# Refresh package database
yum -y --nogpgcheck makecache

# Download OBS Light and its dependencies, without installing them
yum -y install yum-plugin-downloadonly
yum -y install --downloadonly obslight

echo "End of OBS Light post-installation script"

