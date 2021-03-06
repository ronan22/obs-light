Name:           emptySpec
Version: 0
Release: 0
License: GPLv2
Summary: An empty spec file used to create a chroot jail
Url: empty
Group: Development/Tools/Building
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
Source: emptyFile

%description
An empty spec file used to create a chroot jail.

%prep

%build

%install
mkdir -p %{buildroot}%{_docdir}
echo "emptySpec is used only to create the chroot jail" > %{buildroot}%{_docdir}/README.emptySpec

%clean
%{?buildroot:%__rm -rf "%{buildroot}"}

%files
%defattr(-,root,root)
%{_docdir}/README.emptySpec

%changelog

