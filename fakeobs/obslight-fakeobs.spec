# 
# Do NOT Edit the Auto-generated Part!
# Generated by: spectacle version 0.23
# 
# >> macros
# << macros

Name:       obslight-fakeobs
Summary:    Python script that acts as an OBS API
Version:    0.2
Release:    1
Group:      Development/Tools/Building
License:    GPLv2
BuildArch:  noarch
URL:        https://meego.gitorious.org/meego-developer-tools/obs-light/trees/master
Source0:    %{name}-%{version}.tar.gz
Source100:  obslight-fakeobs.yaml
Requires:   apache2
Requires:   git
Requires:   osc
Requires:   python
Requires:   python-async
Requires:   python-gitdb
Requires:   python-gitpython
Requires:   python-smmap
Requires(post): /sbin/service
Requires(post): /sbin/chkconfig
Requires(postun): /sbin/service
Requires(postun): /sbin/chkconfig


%description
Python script that partially implement an OBS API.
It is based on Mer Delivery System.




%prep
%setup -q -n %{name}-%{version}

# >> setup
# << setup

%build
# >> build pre
# << build pre



# >> build post
# << build post
%install
rm -rf %{buildroot}
# >> install pre
mkdir -p %{buildroot}/srv/fakeobs/obs-projects
mkdir -p %{buildroot}/srv/fakeobs/obs-repos
mkdir -p %{buildroot}/srv/fakeobs/packages-git
mkdir -p %{buildroot}/srv/fakeobs/releases
mkdir -p %{buildroot}%{_sysconfdir}/init.d
mkdir -p %{buildroot}%{_sbindir}
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_docdir}%{name}
cp -rf tools %{buildroot}/srv/fakeobs/tools
cp -rf config %{buildroot}/srv/fakeobs/config
cp -f obslight-fakeobs %{buildroot}%{_bindir}
cp -f init_fakeobs %{buildroot}%{_sysconfdir}/init.d/fakeobs
cp -f README %{buildroot}%{_docdir}%{name}

ln -sf /srv/fakeobs/tools/fakeobs.py %{buildroot}%{_sbindir}/fakeobs
ln -sf %{_sysconfdir}/init.d/fakeobs %{buildroot}%{_sbindir}/rcfakeobs

# << install pre

# >> install post
# << install post


%preun
# >> preun
%stop_on_removal fakeobs
if [ $1 -eq 0 ] ; then
  /sbin/chkconfig --del fakeobs
fi
# << preun

%post
# >> post
cd /srv/fakeobs/
if [ ! -f lastevents ]
then
touch lastevents
sh tools/addevent initial na na
fi

if [ ! -f mappings.xml ]
then
echo -e "<mappings>\n</mappings>" > mappings.xml
fi

if [ -d %{_sysconfdir}/apache2/vhosts.d ]
then
ln -sf /srv/fakeobs/config/fakeobs-repos.apache2conf %{_sysconfdir}/apache2/vhosts.d/fakeobs-repos.conf
fi
if [ -d %{_sysconfdir}/lighttpd/vhosts.d ]
then
ln -sf /srv/fakeobs/config/fakeobs-repos.lighttpdconf %{_sysconfdir}/lighttpd/vhosts.d/fakeobs-repos.conf
fi
#/sbin/chkconfig --add fakeobs
# << post

%postun
# >> postun
%restart_on_update fakeobs
%insserv_cleanup
# << postun


%files
%defattr(-,root,root,-)
# >> files
%dir /srv/fakeobs
%dir /srv/fakeobs/obs-projects
%dir /srv/fakeobs/obs-repos
%dir /srv/fakeobs/packages-git
%dir /srv/fakeobs/releases
%dir /srv/fakeobs/tools
%dir /srv/fakeobs/config
/srv/fakeobs/tools/*
/srv/fakeobs/config/*
%config %{_sysconfdir}/init.d/fakeobs
%{_sbindir}/fakeobs
%{_sbindir}/rcfakeobs
%{_bindir}/obslight-fakeobs
%{_docdir}%{name}
# << files

