# 
# Do NOT Edit the Auto-generated Part!
# Generated by: spectacle version 0.23
# 
# >> macros
# << macros

Name:       obslight-fakeobs
Summary:    Python script that acts as an OBS API
Version:    1.0.0
Release:    1
Group:      Development/Tools/Building
License:    GPLv2
BuildArch:  noarch
URL:        https://meego.gitorious.org/meego-developer-tools/obs-light/trees/master
Source0:    %{name}-%{version}.tar.gz
Source100:  obslight-fakeobs.yaml
%if 0%{?fedora}
Requires:   httpd
Requires:   redhat-lsb
BuildRequires: systemd-units
Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units
%else
Requires:   apache2
Requires(post): sysconfig
%endif

Requires:   createrepo
Requires:   logrotate
Requires:   osc
Requires:   python
Requires:   python-cmdln

Requires(post): /sbin/service
Requires(post): /sbin/chkconfig
Requires(postun): /sbin/service
Requires(postun): /sbin/chkconfig

BuildRequires: python
BuildRequires: python-devel
%description
Python script that partially implement an OBS API.
It is based on Mer Delivery System.




%prep
%setup -q -n %{name}

# >> setup
# << setup

%build
# >> build pre
CFLAGS="$RPM_OPT_FLAGS" %{__python} setup.py build
# << build pre



# >> build post
# << build post
%install
rm -rf %{buildroot}
# >> install pre
mkdir -p %{buildroot}/srv/obslight-fakeobs/projects
mkdir -p %{buildroot}/srv/obslight-fakeobs/repositories
mkdir -p %{buildroot}/srv/obslight-fakeobs/tools
mkdir -p %{buildroot}%{_sysconfdir}/logrotate.d
mkdir -p %{buildroot}%{_sbindir}
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_docdir}/%{name}

%if 0%{?suse_version}
%{__python} setup.py install --root=%{buildroot} --prefix=%{_prefix}
%else
%{__python} setup.py install --root=%{buildroot} -O1
%endif

%if 0%{?fedora}
mkdir -p %{buildroot}%{_unitdir}
cp -f config/fakeobs.service config/fakeobswebui.service %{buildroot}%{_unitdir}
%else
mkdir -p %{buildroot}%{_sysconfdir}/init.d
cp -f config/init_fakeobs %{buildroot}%{_sysconfdir}/init.d/fakeobs
cp -f config/init_fakeobswebui %{buildroot}%{_sysconfdir}/init.d/fakeobswebui
%endif
# The following 3 lines are already executed by setup.py
#cp -rf config %{buildroot}/srv/obslight-fakeobs/config
#cp -rf theme %{buildroot}/srv/obslight-fakeobs/theme
#cp -rf tools %{buildroot}/srv/obslight-fakeobs/tools
cp -f config/logrotate_fakeobs %{buildroot}%{_sysconfdir}/logrotate.d/fakeobs
cp -f README %{buildroot}%{_docdir}/%{name}
echo "%{name}-%{version}-%{release}" > %{buildroot}%{_docdir}/%{name}/VERSION

ln -sf %{_sysconfdir}/init.d/fakeobs %{buildroot}%{_sbindir}/rcfakeobs
ln -sf %{_sysconfdir}/init.d/fakeobswebui %{buildroot}%{_sbindir}/rcfakeobswebui

# << install pre

# >> install post
# << install post


%preun
# >> preun
%if 0%{?fedora}
if [ $1 -eq 0 ] ; then
  # Package removal, not upgrade
  /bin/systemctl --no-reload disable fakeobs.service > /dev/null 2>&1 || :
  /bin/systemctl --no-reload disable fakeobswebui.service > /dev/null 2>&1 || :
  /bin/systemctl stop fakeobs.service > /dev/null 2>&1 || :
  /bin/systemctl stop fakeobswebui.service > /dev/null 2>&1 || :
fi
%else
%stop_on_removal fakeobs
%stop_on_removal fakeobswebui
if [ $1 -eq 0 ] ; then
/sbin/chkconfig --del fakeobs
/sbin/chkconfig --del fakeobswebui
fi
%endif
# << preun

%post
# >> post
cd /srv/obslight-fakeobs/
if [ ! -f lastevents ]
then
touch lastevents
# sh tools/addevent initial na na
fi

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
ln -sf /srv/obslight-fakeobs/config/fakeobs-repos.apache2conf "$APACHEVHOST"/fakeobs-repos.conf
fi
if [ -d %{_sysconfdir}/lighttpd/vhosts.d ]
then
ln -sf /srv/obslight-fakeobs/config/fakeobs-repos.lighttpdconf %{_sysconfdir}/lighttpd/vhosts.d/fakeobs-repos.conf
fi

OVERVIEW="/srv/www/obs/overview/index.html"
if [ -f $OVERVIEW ]
then
if ! $(grep -q fakeobs $OVERVIEW)
then
cat >> $OVERVIEW << EOF
<p><a href=http://obslightserver:8001>The fakeobs API URL(http://obslightserver:8001)</a> is used by the "fakeobs" project link.</p>
<p><a href=http://obslightserver:8002>The fakeobs repositories</a> contain the static build results, the repositories can be added to package managers like zypper or apt.</p>
EOF
fi
fi

%if 0%{?fedora}
if [ $1 -eq 1 ] ; then
  # Initial installation
  /bin/systemctl enable fakeobs.service >/dev/null 2>&1 || :
  /bin/systemctl enable fakeobswebui.service >/dev/null 2>&1 || :
fi
%else
# Remove old http python server service
[ -e /etc/init.d/obslightserver ] && service obslightserver status >/dev/null && service obslightserver stop || :
[ -e /etc/init.d/obslightserver ] && /sbin/chkconfig --check obslightserver && /sbin/chkconfig --del obslightserver || :

%{fillup_and_insserv -f -y fakeobs}
%{fillup_and_insserv -f -y fakeobswebui}
%restart_on_update fakeobs
%restart_on_update fakeobswebui
# Starting services also on first install
service fakeobs status || service fakeobs start || :
service fakeobswebui status || service fakeobswebui start || :

# Make apache2 start automatically after installation (and at reboot)
[ -e /etc/init.d/apache2 ] && /sbin/chkconfig --add apache2 || :
[ -e /etc/init.d/apache2 ] && service apache2 start || :

%endif
# << post

%postun
# >> postun
%if 0%{?fedora}
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
if [ $1 -ge 1 ] ; then
  # Package upgrade, not uninstall
  /bin/systemctl try-restart fakeobs.service >/dev/null 2>&1 || :
  /bin/systemctl try-restart fakeobswebui.service >/dev/null 2>&1 || :
fi
%else
%insserv_cleanup
%endif

OVERVIEW="/srv/www/obs/overview/index.html"
if [ "$1" -eq "0" ]
then
if [ -f $OVERVIEW ]
then
if $(grep -q fakeobs $OVERVIEW)
then
cp -f "$OVERVIEW" "$OVERVIEW.old"
grep -v fakeobs "$OVERVIEW.old" > "$OVERVIEW"
fi
fi
fi
# << postun


%files
%defattr(-,root,root,-)
# >> files
%dir /srv/obslight-fakeobs
%dir /srv/obslight-fakeobs/projects
%dir /srv/obslight-fakeobs/repositories
%dir /srv/obslight-fakeobs/config
%dir /srv/obslight-fakeobs/theme
%dir /srv/obslight-fakeobs/tools
/srv/obslight-fakeobs/config/*
/srv/obslight-fakeobs/theme/*
/srv/obslight-fakeobs/tools/*
%{py_sitedir}/ObsLightFakeObs
%{py_sitedir}/obslight_fakeobs-*.egg-info
%if 0%{?fedora}
%{_unitdir}/fakeobs.service
%{_unitdir}/fakeobswebui.service
%else
%config %{_sysconfdir}/init.d/fakeobs
%config %{_sysconfdir}/init.d/fakeobswebui
%endif
%config %{_sysconfdir}/logrotate.d/fakeobs
%config %{_sysconfdir}/obslight-fakeobs.conf
%{_sbindir}/obslight-fakeobsd
%{_sbindir}/obslight-fakeobswebuid
%{_sbindir}/rcfakeobs
%{_sbindir}/rcfakeobswebui
%{_bindir}/obslight-fakeobs
%{_docdir}/%{name}
# << files


