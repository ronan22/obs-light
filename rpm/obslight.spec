# 
# Do NOT Edit the Auto-generated Part!
# Generated by: spectacle version 0.23
# 
# >> macros
%define name obslight
%define version 0.4.6
%define unmangled_version 0.4.6
%define release 1
# << macros

%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
Name:       %{name}
Summary:    OBS Light
Version:    %{version}
Release:    %{release}
Group:      Development/Tools/Building
License:    GPLv2
BuildArch:  noarch
Prefix:  %{_prefix}
URL:        http://wiki.meego.com/OBS_Light
Source0:    %{name}-%{unmangled_version}.tar.gz
Source100:  %{name}.yaml
Requires:   python >= 2.5.0
BuildRequires:  python >= 2.5.0
BuildRequires:  python-devel >= 2.5.0
BuildRequires:  fdupes


%description
Utilities to work with OBS Light, a lighter version of OBS.


%package gui
Summary:    Utilities to work with OBS Light - graphical interface
Group:      Development/Tools/Building
Requires:   %{name} = %{version}-%{release}
Requires:   python >= 2.5.0
Requires:   obslight-base
Requires:   python-pyside

%description gui
Utilities to work with OBS Light, a lighter version of OBS.
This package contains the graphical interface.


%package base
Summary:    Utilities to work with OBS Light - command-line client
Group:      Development/Tools/Building
Requires:   %{name} = %{version}-%{release}
Requires:   python >= 2.5.0
Requires:   python-xml
Requires:   meego-packaging-tools
Requires:   sudo
Requires:   qemu
Requires:   spectacle
Provides:   obslight

%description base
Utilities to work with OBS Light, a lighter version of OBS.
This package contains the command-line client.


%package utils
Summary:    Utilities to work with OBS Light - additional scripts
Group:      Development/Tools/Building
Requires:   %{name} = %{version}-%{release}
Requires:   python >= 2.5.0
Requires:   python-xml
Requires:   osc

%description utils
Utilities to work with OBS Light, a lighter version of OBS.
This package contains additional scripts :
 - obstag:           Tag a project in an OBS
 - obs2obscopy:      Copy a project from an OBS to an OBS
 - obsextractgroups: Extracts the packages groups of an OBS repository



%prep
%setup -q -n %{name}-%{version}

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
%{__python} setup.py install --root=%{buildroot} -O1

# >> install post
%fdupes -s $RPM_BUILD_ROOT/%{python_sitelib}
ln -s obslight-wrapper.py %{buildroot}/%{_bindir}/obslight
ln -s obslightgui-wrapper.py %{buildroot}/%{_bindir}/obslightgui

# << install post









%preun base
# >> preun base
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
# << preun base

%post base
# >> post base
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
# << post base





%files
%defattr(-,root,root,-)
# >> files
# << files


%files gui
%defattr(-,root,root,-)
# >> files gui
%{_bindir}/obslightgui
%{_bindir}/obslightgui-wrapper.py
%{python_sitelib}/ObsLightGui
# << files gui

%files base
%defattr(-,root,root,-)
# >> files base
%doc README VERSION
%{_bindir}/obslight
%{_bindir}/obslight-wrapper.py
%{python_sitelib}/ObsLight
%{python_sitelib}/obslight*egg-info
%config %attr(440, root, root) %{_sysconfdir}/sudoers.obslight
%config %{_sysconfdir}/bash_completion.d/obslight.sh
# << files base

%files utils
%defattr(-,root,root,-)
# >> files utils
%{_bindir}/obs2obscopy
%{_bindir}/obstag
%{_bindir}/obsextractgroups
# << files utils

