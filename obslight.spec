%define name obslight
%define version 0.3
%define unmangled_version 0.3
%define release 1

Summary: OBS Light
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{unmangled_version}.tar.gz
License: GPLv2
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Ronan Le Martret <ronan@fridu.net>
Url: http://wiki.meego.com/OBS_Light
BuildRequires: python
BuildRequires: osc
BuildRequires: python-xml
Requires: python
Requires: meego-packaging-tools
Requires: python-xml
Requires: sudo
Requires: qemu
%{!?python_sitelib: %define python_sitelib %(python -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

%description
Command-line client and UI for the OBS.

%prep
%setup -n %{name}-%{unmangled_version}

%build
python setup.py build

%install
python setup.py install -O1 --root=%{buildroot} --prefix=%{_prefix}
ln -s obslight-wrapper.py %{buildroot}/%{_bindir}/obslight
ln -s obslightgui-wrapper.py %{buildroot}/%{_bindir}/obslight-gui

%post
if [ ! -f "%{_sysconfdir}/sudoers.tmp" ]; then
  touch %{_sysconfdir}/sudoers.tmp
  [ -f %{_sysconfdir}/sudoers ] && cp %{_sysconfdir}/sudoers %{_sysconfdir}/sudoers.new
  echo "%users ALL=(ALL)NOPASSWD:/usr/bin/build" >> %{_sysconfdir}/sudoers.new
#  %{_sbindir}/visudo -c -f %{_sysconfdir}/sudoers.new
#  [ "$?" -eq "0" ] && cp %{_sysconfdir}/sudoers.new %{_sysconfdir}/sudoers
  cp %{_sysconfdir}/sudoers.new %{_sysconfdir}/sudoers
  rm %{_sysconfdir}/sudoers.tmp
fi

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc README
%{_bindir}/obslight*
%{_bindir}/obs2obscopy
%{_bindir}/obstag
%{_bindir}/obsextractgroups
%{python_sitelib}/*
