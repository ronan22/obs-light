Name:           emptySpec
Version: 0
Release: 0
License: GPLv2
Summary: empty
Url: empty
Group: empty
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
Source: emptyFile

%description

%prep

%build

%install

%clean
%{?buildroot:%__rm -rf "%{buildroot}"}

%post

%postun

%files
%defattr(-,root,root)

%changelog

