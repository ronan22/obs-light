# 
# Do NOT Edit the Auto-generated Part!
# Generated by: spectacle version 0.23
# 
# >> macros
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
# << macros

Name:       obslight-fakeobs
Summary:    Python script that acts as an OBS API
Version:    1.0.2
Release:    1
Group:      Development/Tools/Building
License:    GPL-2.0
BuildArch:  noarch
URL:        https://meego.gitorious.org/meego-developer-tools/obs-light/trees/master
Source0:    %{name}-%{version}.tar.gz
Source100:  obslight-fakeobs.yaml

%if 0%{?fedora}
AutoReqProv: no
Requires:   httpd
Requires:   redhat-lsb
Requires:   GitPython
BuildRequires: systemd-units
Requires(post): python-setuptools
Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units
%else
Requires:   apache2
Requires:   python-cmdln
Requires(post): sysconfig
%endif

%if 0%{?suse_version} >= 1210
BuildRequires: systemd
%{?systemd_requires}
%endif

Requires:   build
Requires:   createrepo
Requires:   logrotate
Requires:   obslight-depsolver
Requires:   osc
Requires:   python
Requires:   rpm

Requires(post): /sbin/service
Requires(post): /sbin/chkconfig
Requires(postun): /sbin/service
Requires(postun): /sbin/chkconfig

BuildRequires: python
BuildRequires: python-devel
%description
Python script that partially implement an OBS API.
It is based on Mer Delivery System.

%package -n obslight-depsolver
Summary: Dependency solving scripts for OBS Light
Group: Development/Tools/Building
Requires:   bash
Requires:   build
Requires:   perl

%description -n obslight-depsolver
Dependency solving scripts for OBS Light.

%prep
%setup -q

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

%if 0%{?fedora} || 0%{?suse_version} >= 1210
mkdir -p %{buildroot}%{_unitdir}
cp -f config/fakeobs.service config/fakeobswebui.service %{buildroot}%{_unitdir}
%else
mkdir -p %{buildroot}%{_sysconfdir}/init.d
cp -f config/init_fakeobs %{buildroot}%{_sysconfdir}/init.d/fakeobs
cp -f config/init_fakeobswebui %{buildroot}%{_sysconfdir}/init.d/fakeobswebui
ln -sf %{_sysconfdir}/init.d/fakeobs %{buildroot}%{_sbindir}/rcfakeobs
ln -sf %{_sysconfdir}/init.d/fakeobswebui %{buildroot}%{_sbindir}/rcfakeobswebui
%endif
# The following 3 lines are already executed by setup.py
#cp -rf config %{buildroot}/srv/obslight-fakeobs/config
#cp -rf theme %{buildroot}/srv/obslight-fakeobs/theme
#cp -rf tools %{buildroot}/srv/obslight-fakeobs/tools
cp -f config/logrotate_fakeobs %{buildroot}%{_sysconfdir}/logrotate.d/obslight-fakeobs
cp -f README %{buildroot}%{_docdir}/%{name}
echo "%{name}-%{version}-%{release}" > %{buildroot}%{_docdir}/%{name}/VERSION
# << install pre

# >> install post
# << install post


%preun
# >> preun
%if 0%{?fedora} || 0%{?suse_version} >= 1210
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
echo "1|$(date +%%s)|initial|na|na|" >> lastevents
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

%if 0%{?fedora} || 0%{?suse_version} >= 1210
if [ $1 -eq 1 ] ; then
  # Initial installation
  /bin/systemctl enable fakeobs.service >/dev/null 2>&1 || :
  /bin/systemctl enable fakeobswebui.service >/dev/null 2>&1 || :

%if 0%{?fedora}
# Fedora doesn't have python-cmdln
  easy_install cmdln
%endif
fi
%else
# Remove old http python server service
[ -e /etc/init.d/obslightserver ] && service obslightserver status >/dev/null && service obslightserver stop || :
[ -e /etc/init.d/obslightserver ] && /sbin/chkconfig --check obslightserver && /sbin/chkconfig --del obslightserver || :
%endif

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

# << post

%postun
# >> postun
%if 0%{?fedora} || 0%{?suse_version} >= 1210
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

%{python_sitelib}/ObsLightFakeObs
%{python_sitelib}/obslight_fakeobs-*.egg-info
%if 0%{?fedora} || 0%{?suse_version} >= 1210
%{_unitdir}/fakeobs.service
%{_unitdir}/fakeobswebui.service
%else
%config %{_sysconfdir}/init.d/fakeobs
%config %{_sysconfdir}/init.d/fakeobswebui
%endif

%config %{_sysconfdir}/logrotate.d/obslight-fakeobs
%config %{_sysconfdir}/obslight-fakeobs.conf
%{_sbindir}/obslight-fakeobsd
%{_sbindir}/obslight-fakeobswebuid
%{_bindir}/obslight-fakeobs
%{_docdir}/%{name}
# << files

%files -n obslight-depsolver
%defattr(-,root,root,-)
%if 0%{?fedora}
#To bypass auto Requires for fedora (require perl(build) but build don't package like this.)
#https://fedoraproject.org/wiki/Packaging:AutoProvidesAndRequiresFiltering#Perl
%{?filter_setup:
%filter_requires_in %{_bindir}/obslight-expanddeps
%filter_requires_in %{_bindir}/obslight-createrpmlistfromspec
%filter_setup
}
%endif

%{_bindir}/obslight-expanddeps
%{_bindir}/obslight-createrpmlistfromspec

