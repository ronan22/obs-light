# 
# Do NOT Edit the Auto-generated Part!
# Generated by: spectacle version 0.23
# 
# >> macros
%{?!fdupes: %define fdupes echo}
%define IMGSRVPATH obslight-image-server
%define REPOSRVPATH obslight-repo-server
# << macros

%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
Name:       obslight
Summary:    OBS Light
Version:    0.9.0
Release:    1
Group:      Development/Tools/Building
License:    GPLv2
BuildArch:  noarch
URL:        http://en.opensuse.org/openSUSE:OBS_Light
Source0:    %{name}-%{version}.tar.gz
Source100:  obslight.yaml
Requires:   acl
Requires:   build
Requires:   createrepo
Requires:   curl
Requires:   gbs >= 0.10
Requires:   git
Requires:   mic >= 0.12
Requires:   osc >= 0.132
Requires:   qemu
Requires:   rpm
Requires:   sudo
Requires:   tightvnc
Requires:   tftp
Requires:   wget
%if 0%{?suse_version} > 1120
Requires:   imagewriter
%endif
%if 0%{?suse_version} > 1140
Requires:   qemu-linux-user
#Requires:   qemu-arm-static
%endif
%if 0%{?fedora}
Requires:   httpd
Requires:   nfs-utils
# qemu-arm-static is not in Fedora repositories but in OBS Light's ones
Requires:   qemu-arm-static
Requires:   redhat-lsb
%else
Requires:   apache2
Requires:   nfs-kernel-server
Requires:   python-xml
%endif
Requires(post): sudo
Requires(post): /sbin/service
Requires(post): /sbin/chkconfig
Requires(postun): sudo
Requires(postun): /sbin/service
Requires(postun): /sbin/chkconfig
BuildRequires:  fdupes
BuildRequires:  python >= 2.6.0
BuildRequires:  python-devel >= 2.6.0
BuildRequires:  rpcbind
BuildRequires:  xinetd
%if 0%{?fedora}
BuildRequires:  nfs-utils
%else
BuildRequires:  nfs-kernel-server
%endif
BuildRequires:  desktop-file-utils
BuildRoot:  %{_tmppath}/%{name}-%{version}-build


%description
Utilities to work with OBS Light, a lighter version of OBS.
This package contains the API, a commandline client,
and some tools (obstag, obs2obscopy, obsextractgroups, obsdodupdate).



%package gui
Summary:    Utilities to work with OBS Light - graphical interface
Group:      Development/Tools/Building
Requires:   %{name} = %{version}-%{release}
Requires:   obslight = %{version}
Requires:   python-pyside >= 1.0.6
Conflicts:  obslight-base
Conflicts:  obslight-server
Conflicts:  obslight-utils

%description gui
Utilities to work with OBS Light, a lighter version of OBS.
This package contains the graphical interface.



%prep
%setup -q

# >> setup
# << setup

%build
# >> build pre
# << build pre

CFLAGS="$RPM_OPT_FLAGS" %{__python} setup.py build

# >> build post
# << build post
%install
rm -rf %{buildroot}
# >> install pre
echo "%{version}-%{release}" > VERSION
# << install pre
%if 0%{?suse_version}
%{__python} setup.py install --root=%{buildroot} --prefix=%{_prefix}
%else
%{__python} setup.py install --root=%{buildroot} -O1
%endif

# >> install post
%fdupes -s %{buildroot}/%{python_sitelib}
ln -s obslight-wrapper.py %{buildroot}/%{_bindir}/obslight
ln -s obslightgui-wrapper.py %{buildroot}/%{_bindir}/obslightgui

install -d %{buildroot}/etc/init.d
# To be removed when we add a theme (would be already created by setup.py)
mkdir -p %{buildroot}/srv/%IMGSRVPATH/www
mkdir -p %{buildroot}/usr/share/obslight/projectTemplate
mkdir -p %{buildroot}/usr/share/obslight/projectConf


# << install post
desktop-file-install --delete-original       \
  --dir %{buildroot}%{_datadir}/applications             \
   %{buildroot}%{_datadir}/applications/*.desktop

%preun
# >> preun
if [ $1 -eq "0" ]
then
  # We are uninstalling OBS Light (not upgrading)
  echo "Trying to remove OBS Light sudoers rule..."
  if [ ! -f "%{_sysconfdir}/sudoers.tmp" ]
  then
    touch %{_sysconfdir}/sudoers.tmp
    sed -i s/"#include .*sudoers\.obslight"// %{_sysconfdir}/sudoers
    rm %{_sysconfdir}/sudoers.tmp
    echo " DONE"
  else
    echo "Cannot modify sudoers file !"
  fi
fi
# << preun

%post
# >> post
echo "Trying to add OBS Light sudoers rule..."
if [ ! -f "%{_sysconfdir}/sudoers.tmp" ]
then
  touch %{_sysconfdir}/sudoers.tmp
  if [ -z "$(grep sudoers.obslight %{_sysconfdir}/sudoers)" ]
  then
    echo "#include %{_sysconfdir}/sudoers.obslight" >> %{_sysconfdir}/sudoers
    echo " DONE"
  else
    echo " sudoers rule already configured"
  fi
  rm %{_sysconfdir}/sudoers.tmp
else
  echo "Cannot modify sudoers file !";
fi

echo "Trying to add OBS Light Image Server..."
[ -d /srv/%IMGSRVPATH/www ] || install -d -o nobody -g users /srv/%IMGSRVPATH/www
[ -d /srv/%REPOSRVPATH/www ] || install -d -o nobody -g users /srv/%REPOSRVPATH/www

echo "/srv/%REPOSRVPATH/www  *(rw,fsid=0,no_root_squash,insecure,no_subtree_check)" >> /etc/exports

/sbin/chkconfig --add xinetd
/sbin/chkconfig --add rpcbind
/sbin/chkconfig --add nfsserver

if [ -d "%{_sysconfdir}/apache2/vhosts.d" ]
then
# openSUSE
  APACHEVHOST="%{_sysconfdir}/apache2/vhosts.d"
elif [ -d "%{_sysconfdir}/httpd/conf.d" ]
then
# Fedora
  APACHEVHOST="%{_sysconfdir}/httpd/conf.d"
fi
if [ -n "$APACHEVHOST" ]
then
ln -sf /srv/%IMGSRVPATH/config/obslight-image.apache2conf $APACHEVHOST/obslight-image.conf
ln -sf /srv/%REPOSRVPATH/config/obslight-repos.apache2conf $APACHEVHOST/obslight-repos.conf
MOD_INCLUDE="/etc/apache2/mods-available/include.load"
[ -f $MOD_INCLUDE ] && ln -sf $MOD_INCLUDE /etc/apache2/mods-enabled/include.load
fi

#Remove old http python server service.
[ -e /etc/init.d/obslightserver ] && service obslightserver status >/dev/null && service obslightserver stop || :
[ -e /etc/init.d/obslightserver ] && /sbin/chkconfig --check obslightserver && /sbin/chkconfig --del obslightserver || :

#Add new http apache2 server service.
[ -e /etc/init.d/apache2 ] && /sbin/chkconfig --add apache2
[ -e /etc/init.d/apache2 ] && service apache2 start

chown nobody:users /srv/%IMGSRVPATH
chown nobody:users /srv/%REPOSRVPATH
chown nobody:users /srv/%IMGSRVPATH/config
chown nobody:users /srv/%REPOSRVPATH/config
chown nobody:users /srv/%IMGSRVPATH/www
chown nobody:users /srv/%REPOSRVPATH/www

chmod g+w /srv/%IMGSRVPATH
chmod g+w /srv/%REPOSRVPATH
chmod g+w /srv/%IMGSRVPATH/config
chmod g+w /srv/%REPOSRVPATH/config
chmod g+w /srv/%IMGSRVPATH/www
chmod g+w /srv/%REPOSRVPATH/www

chmod -R o+rw /usr/share/obslight
# << post

%files
%defattr(-,root,root,-)
# >> files
%doc README VERSION
%{_bindir}/obs2obscopy
%{_bindir}/obstag
%{_bindir}/obsextractgroups
%{_bindir}/obsdodupdate
%{_bindir}/obsprojectsdiff
%{_bindir}/obslight
%{_bindir}/obslight-wrapper.py
%{_bindir}/generate_default_xml
%{python_sitelib}/ObsLight
%{python_sitelib}/obslight*egg-info
%config %attr(440, root, root) %{_sysconfdir}/sudoers.obslight
%config %{_sysconfdir}/bash_completion.d/obslight.sh
%config %{_sysconfdir}/xinetd.d/tftp

%dir /srv/%IMGSRVPATH
%dir /srv/%REPOSRVPATH
%dir /srv/%IMGSRVPATH/config
%dir /srv/%REPOSRVPATH/config
%dir /srv/%IMGSRVPATH/www
%dir /srv/%REPOSRVPATH/www
%dir /srv/%REPOSRVPATH/www/theme
%dir /srv/%REPOSRVPATH/www/theme/images
%dir /usr/share/obslight
%dir /usr/share/obslight/projectTemplate
%dir /usr/share/obslight/projectConf

/srv/%IMGSRVPATH/config/obslight-image.apache2conf
/srv/%REPOSRVPATH/config/obslight-repos.apache2conf
/srv/%REPOSRVPATH/www/theme/*
/srv/%REPOSRVPATH/www/theme/images/*

/usr/share/obslight/projectConf/*
/usr/share/obslight/projectTemplate/*
# << files

%files gui
%defattr(-,root,root,-)
# >> files gui
%{_bindir}/obslightgui
%{_bindir}/obslightgui-wrapper.py
%{python_sitelib}/ObsLightGui
%{_datadir}/applications/obslightgui.desktop
%{_datadir}/pixmaps/obslight.png
# << files gui

