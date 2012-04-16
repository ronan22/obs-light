#!/bin/sh

date > /etc/vagrant_box_build_time

# install vagrant key
echo -e "\ninstall vagrant key ..."
mkdir -m 0700 /home/vagrant/.ssh
cd /home/vagrant/.ssh
wget --no-check-certificate -O authorized_keys https://raw.github.com/mitchellh/vagrant/master/keys/vagrant.pub
chmod 0600 /home/vagrant/.ssh/authorized_keys
chown -R vagrant.users /home/vagrant/.ssh

# update sudoers
echo -e "\nupdate sudoers ..."
echo -e "\n# added by veewee/postinstall.sh" >> /etc/sudoers
echo -e "vagrant ALL=(ALL) NOPASSWD: ALL\n" >> /etc/sudoers

VBOX_VERSION=$(cat /home/vagrant/.vbox_version)

#yum -y --exclude=kernel* update
yum -y update

yum -y install \
  ruby \
  ruby-devel \
  puppet \
  rubygems \
  rubygem-erubis \
  rubygem-highline \
  rubygem-json \
  rubygem-mime-types \
  rubygem-net-ssh \
  rubygem-polyglot \
  rubygem-rest-client \
  rubygem-treetop \
  rubygem-uuidtools

#   VirtualBox guest additions installation should be done after reboot,
#   with the new kernel.
# cd /tmp
# wget http://download.virtualbox.org/virtualbox/$VBOX_VERSION/VBoxGuestAdditions_$VBOX_VERSION.iso
# mount -o loop,ro VBoxGuestAdditions_$VBOX_VERSION.iso /mnt
# sh /mnt/VBoxLinuxAdditions.run
# umount /mnt
# rm VBoxGuestAdditions_$VBOX_VERSION.iso

gem install chef --no-rdoc --no-ri

reboot

sleep 10
exit

# EOF
