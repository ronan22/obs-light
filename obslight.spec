%define name obslight
%define version 0.3.3
%define unmangled_version 0.3.3
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

%build
python setup.py build

%install
python setup.py install -O1 --root=%{buildroot} --prefix=%{_prefix}
%fdupes -s $RPM_BUILD_ROOT/%{python_sitelib}
ln -s obslight-wrapper.py %{buildroot}/%{_bindir}/obslight
ln -s obslightgui-wrapper.py %{buildroot}/%{_bindir}/obslightgui

%post base
if [ ! -f "%{_sysconfdir}/sudoers.tmp" ]; then
  touch %{_sysconfdir}/sudoers.tmp
  if [ -z "$(grep sudoers.obslight %{_sysconfdir}/sudoers)" ]; then
    echo "#include %{_sysconfdir}/sudoers.obslight" >> %{_sysconfdir}/sudoers
  fi
  rm %{_sysconfdir}/sudoers.tmp
fi

%clean
rm -rf %{buildroot}

%files base
%defattr(-,root,root)
%doc README
%config %{_sysconfdir}/sudoers.obslight
%{_bindir}/obslight
%{_bindir}/obslight-wrapper.py
%{python_sitelib}/ObsLight
%{python_sitelib}/obslight*egg-info

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
* Thu Oct 20 2011 Florent Vennetier (Intel OTC) <florent@fridu.net> 0.3.3-1
- Improved (fixed?) patch generation

* Wed Oct 19 2011 Florent Vennetier (Intel OTC) <florent@fridu.net> 0.3.2-1
- Modified sudo rules so that user doesn't have to type passwords

* Wed Oct 19 2011 Florent Vennetier (Intel OTC) <florent@fridu.net> 0.3.1-1
- Added some internal tests

* Mon Oct 17 2011 Florent Vennetier (Intel OTC) <florent@fridu.net> 0.3-1
- First public version
