%define name obslight
%define version 0.4.2
%define unmangled_version 0.4.2
%define release 1

Summary: OBS Light
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{unmangled_version}.tar.gz
License: GPLv2
Group: Development/Tools/Building
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Intel Open Source Technology Center (OTC)
Url: http://wiki.meego.com/OBS_Light
BuildRequires: python >= 2.5.0
BuildRequires: python-devel >= 2.5.0
BuildRequires: fdupes
Requires: python >= 2.5.0
%if 0%{?suse_version}
%py_requires
%endif
%{!?python_sitelib: %define python_sitelib %(python -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

%description
Utilities to work with OBS Light, a lighter version of OBS.

%package base
BuildRequires: python-devel >= 2.5.0
Requires: python >= 2.5.0
Requires: python-xml
Requires: meego-packaging-tools
Requires: sudo
Requires: qemu
Requires: spectacle
Summary: Utilities to work with OBS Light - command-line client
Provides: obslight
%description base
Utilities to work with OBS Light, a lighter version of OBS.
This package contains the command-line client.

%package gui
BuildRequires: python-devel >= 2.5.0
Requires: python >= 2.5.0
Requires: obslight-base
Requires: python-pyside
Summary: Utilities to work with OBS Light - graphical interface
%description gui
Utilities to work with OBS Light, a lighter version of OBS.
This package contains the graphical interface.

%package utils
Requires: python >= 2.5.0
Requires: python-xml
Requires: osc
Summary: Utilities to work with OBS Light - additional scripts
%description utils
Utilities to work with OBS Light, a lighter version of OBS.
This package contains additional scripts :
 - obstag:           Tag a project in an OBS
 - obs2obscopy:      Copy a project from an OBS to an OBS
 - obsextractgroups: Extracts the packages groups of an OBS repository

%prep
%setup -n %{name}-%{unmangled_version}
sed -i s/"VERSION = .*"/"VERSION = \"0.4.2-1.2\""/ ObsLight/ObsLightManager.py

%build
python setup.py build

%install
echo "%{version}-%{release}" > VERSION
python setup.py install -O1 --root=%{buildroot} --prefix=%{_prefix}
%fdupes -s $RPM_BUILD_ROOT/%{python_sitelib}
ln -s obslight-wrapper.py %{buildroot}/%{_bindir}/obslight
ln -s obslightgui-wrapper.py %{buildroot}/%{_bindir}/obslightgui

%post base
echo "Trying to add OBS Light sudoers rule..."
if [ ! -f "%{_sysconfdir}/sudoers.tmp" ]; then
  touch %{_sysconfdir}/sudoers.tmp
  if [ -z "$(grep sudoers.obslight %{_sysconfdir}/sudoers)" ]; then
    echo "#include %{_sysconfdir}/sudoers.obslight" >> %{_sysconfdir}/sudoers
    echo " DONE"
  else
    echo " sudoers rule already configured"
  fi
  rm %{_sysconfdir}/sudoers.tmp
else
  echo "Cannot modify sudoers file";
fi

%preun base
echo "Trying to remove OBS Light sudoers rule..."
if [ $1 -eq "0" ]; then
  if [ ! -f "%{_sysconfdir}/sudoers.tmp" ]; then
    touch %{_sysconfdir}/sudoers.tmp
    sed -i s/"#include .*sudoers\.obslight"// %{_sysconfdir}/sudoers
    rm %{_sysconfdir}/sudoers.tmp
    echo " DONE"
  else
    echo "Cannot modify sudoers file"
  fi
else
  echo " just updating, sudoers rule not modified"
fi

%clean
rm -rf %{buildroot}

%files base
%defattr(-,root,root)
%doc README VERSION
%{_bindir}/obslight
%{_bindir}/obslight-wrapper.py
%{python_sitelib}/ObsLight
%{python_sitelib}/obslight*egg-info
%config %attr(440, root, root) %{_sysconfdir}/sudoers.obslight
%config %{_sysconfdir}/bash_completion.d/obslight.sh

%files gui
%defattr(-,root,root)
%{_bindir}/obslightgui
%{_bindir}/obslightgui-wrapper.py
%{python_sitelib}/ObsLightGui

%files utils
%defattr(-,root,root)
%{_bindir}/obs2obscopy
%{_bindir}/obstag
%{_bindir}/obsextractgroups

%changelog
* Fri Nov 18 2011 Florent Vennetier (Intel OTC) <florent@fridu.net> 0.4.2-1
- added check connection button
- fixed unicode problems

* Thu Nov 17 2011 Florent Vennetier (Intel OTC) <florent@fridu.net> 0.4.1-1
- Working GUI

* Wed Oct 27 2011 Ronan Le Martret (Intel OTC) <ronan@fridu.net> 0.4.0-2
- Add completion 

* Wed Oct 26 2011 Florent Vennetier (Intel OTC) <florent@fridu.net> 0.4.0-1
- First stable version

* Mon Oct 24 2011 Florent Vennetier (Intel OTC) <florent@fridu.net> 0.3.4-1
- Improved sudo rules
- New debug/verbose options

* Thu Oct 20 2011 Florent Vennetier (Intel OTC) <florent@fridu.net> 0.3.3-1
- Improved (fixed?) patch generation

* Wed Oct 19 2011 Florent Vennetier (Intel OTC) <florent@fridu.net> 0.3.2-1
- Modified sudo rules so that user doesn't have to type passwords

* Wed Oct 19 2011 Florent Vennetier (Intel OTC) <florent@fridu.net> 0.3.1-1
- Added some internal tests

* Mon Oct 17 2011 Florent Vennetier (Intel OTC) <florent@fridu.net> 0.3-1
- First public version
