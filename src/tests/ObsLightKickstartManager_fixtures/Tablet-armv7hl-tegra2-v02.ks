# -*-mic2-options-*- -f raw --save-kernel --arch=armv7hl -*-mic2-options-*-

lang en_US.UTF-8
keyboard us
timezone --utc America/Los_Angeles
auth --useshadow --enablemd5

part /boot --size 64 --ondisk mmcblk0p --fstype=ext2 --active
part / --size 1600 --ondisk mmcblk0p --fstype=ext3

rootpw meego
xconfig --startxonboot
desktop --autologinuser=meego  
user --name meego  --groups audio,video --password meego

#repo --name=1.2-oss --baseurl=http://repo.meego.com/MeeGo/builds/1.1.99/@BUILD_ID@/repos/oss/armv7hl/packages/ --save --debuginfo --source --gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-meego
#repo --name=1.2-non-oss --baseurl=http://repo.meego.com/MeeGo/builds/1.1.99/@BUILD_ID@/repos/non-oss/armv7hl/packages/ --save --debuginfo --source --gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-meego

repo --name=1.2-oss --baseurl=http://download.meego.com/snapshots/1.2.0.90.8.20110713.4/repos/oss/armv7hl/packages/ --save --debuginfo --source --gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-meego
repo --name=1.2-non-oss --baseurl=http://download.meego.com/snapshots/1.2.0.90.8.20110713.4/repos/non-oss/armv7hl/packages/ --save --debuginfo --source --gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-meego

#repo --name=tegraglibc         --baseurl=http://repo.pub.meego.com/home:/vgrade:/glibc/Project_DE_MeeGo_1.2_standard/
#stskeeps glibc http://download.meego.com/live/home:/cvm:/branches:/MeeGo:/1.2:/oss/standard/armv7hl/

%packages --ignoremissing

@MeeGo Core
@MeeGo X Window System
@MeeGo Tablet
@MeeGo Tablet Applications
@X for Netbooks
@MeeGo Base Development
@Development Tools
xorg-x11-drv-mtev
qt-demos
xinput_calibrator
evtest
# Gfx accelleration - use s/w for the timebeing
#mesa-dri-swrast-driver
#xorg-x11-drv-fbdev
xorg-x11-drv-evdev
xorg-x11-utils-xinput
xorg-x11-utils-xev
#mesa-libEGL
mesa-libGL
#mesa-libGLESv2

-dsme
-libdsme
%end

%post
# save a little bit of space at least...
rm -f /boot/initrd*

rm -f /var/lib/rpm/__db*
rpm --rebuilddb

echo "DISPLAYMANAGER=\"uxlaunch\"" >> /etc/sysconfig/desktop
echo "session=/usr/bin/mcompositor" >> /etc/sysconfig/uxlaunch

#echo "xopts=-nocursor" >> /etc/sysconfig/uxlaunch

gconftool-2 --direct \
  --config-source xml:readwrite:/etc/gconf/gconf.xml.mandatory \
  -s -t string /meegotouch/target/name tablet

gconftool-2 --direct \
  --config-source xml:readwrite:/etc/gconf/gconf.xml.mandatory \
  -s -t string /meego/ux/theme 1024-600-10

gconftool-2 --direct \
  --config-source xml:readwrite:/etc/gconf/gconf.xml.defaults \
  -s -t bool /meego/ux/ShowPanelsAsHome false

# Copy boot and shutdown images
cp /usr/share/themes/1024-600-10/images/system/boot-screen.png /usr/share/plymouth/splash.png
cp /usr/share/themes/1024-600-10/images/system/shutdown-screen.png /usr/share/plymouth/shutdown-1024x600.png

%end

%post --nochroot
if [ -n "$IMG_NAME" ]; then
    echo "BUILD: $IMG_NAME" >> $INSTALL_ROOT/etc/meego-release
fi
#echo 'export M_USE_SOFTWARE_RENDERING=1' >> $INSTALL_ROOT/home/meego/.bashrc

cat << OMAPFB >> $INSTALL_ROOT/etc/X11/xorg.conf.d/00-input-trimslice.conf
Section "InputClass"
        Identifier "evdev pointer catchall"
        MatchIsPointer "on"
        MatchDevicePath "/dev/input/event*"
        Driver "evdev"
EndSection

Section "InputClass"
        Identifier "evdev keyboard catchall"
        MatchIsKeyboard "on"
        MatchDevicePath "/dev/input/event*"
        Driver "evdev"
EndSection

Section "InputClass"
        Identifier "evdev touchpad catchall"
        MatchIsTouchpad "on"
        MatchDevicePath "/dev/input/event*"
        Driver "evdev"
EndSection

Section "InputClass"
        Identifier "evdev tablet catchall"
        MatchIsTablet "on"
        MatchDevicePath "/dev/input/event*"
        Driver "evdev"
EndSection

Section "InputClass"
        Identifier "evdev touchscreen catchall"
        MatchIsTouchscreen "on"
        MatchDevicePath "/dev/input/event*"
        Driver "evdev"
EndSection
OMAPFB

# Add Meego to sudoers list
cat << SUDOERS >> $INSTALL_ROOT/etc/sudoers
meego ALL=(ALL) ALL
SUDOERS
%end
