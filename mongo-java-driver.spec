%{?scl:%scl_package mongo-java-driver}
%{!?scl:%global pkg_name %{name}}

%if 0%{?rhel}
# Use java common's requires/provides generator
%{?java_common_find_provides_and_requires}
%endif

%global buildscls %{scl_maven} %{scl}

Name:		%{?scl_prefix}mongo-java-driver
Version:	3.5.0
Release:	3%{?dist}
Summary:	A Java driver for MongoDB

Group:		Development/Libraries
BuildArch:	noarch
License:	ASL 2.0
URL:		http://www.mongodb.org/display/DOCS/Java+Language+Center
Source0:	https://github.com/mongodb/%{pkg_name}/archive/r%{version}.tar.gz

Patch0:         0001-Maven-support.patch
Patch1:         0002-Netty-update-workaround.patch

# since 3.4.2 Java 8 is required
BuildRequires:	java-1.8.0-openjdk-devel
BuildRequires:  %{?scl_prefix_maven}maven-local
BuildRequires:  %{?scl_prefix_java_common}mvn(io.netty:netty-buffer)
BuildRequires:  %{?scl_prefix_java_common}mvn(io.netty:netty-transport)
BuildRequires:  %{?scl_prefix_java_common}mvn(io.netty:netty-handler)
BuildRequires:  %{?scl_prefix_java_common}mvn(org.slf4j:slf4j-api)
BuildRequires:  %{?scl_prefix_java_common}mvn(org.hamcrest:hamcrest-library)
BuildRequires:  %{?scl_prefix_maven}mvn(org.apache.maven.plugins:maven-shade-plugin)
BuildRequires:  %{?scl_prefix_maven}mvn(org.apache.felix:maven-bundle-plugin)

%description
This is the Java driver for MongoDB.

%package bson
Summary:	A Java-based BSON implementation
Group:		Development/Libraries

%description bson
This is the Java implementation of BSON that the Java driver for
MongoDB ships with.  It can be used separately by Java applications
that require BSON.
# Upstream has hinted that eventually, their bson implementation will
# be better separated out: http://bsonspec.org/#/implementation
# To make things easier for when that does happen, for now the jar
# and javadocs for this are in separate subpackages.

%package driver
Summary:	The MongoDB Java Driver
Group:		Development/Libraries

%description driver
The MongoDB Java Driver

%package driver-core
Summary:	The MongoDB Java Operations Layer
Group:		Development/Libraries

%description driver-core
The Java operations layer for the MongoDB Java Driver. Third
parties can wrap this layer to provide custom higher-level APIs

%package driver-async
Summary:	The MongoDB Java Async Driver
Group:		Development/Libraries

%description driver-async
The MongoDB Asynchronous Driver.

%package javadoc
Summary:	Javadoc for %{name}
Group:		Documentation

%description javadoc
This package contains the API documentation for %{name}.

%prep
%{?scl:scl enable %{buildscls} - << "EOF"}
%setup -qn %{pkg_name}-r%{version}

%patch0 -p1
%patch1 -p1

sed -i 's/@VERSION@/%{version}/g' `find -name pom.xml`

find -name '*.class' -exec rm -f '{}' \;
find -name '*.jar' -exec rm -f '{}' \;
set -ex
%mvn_package org.mongodb:bson:* %{pkg_name}-bson
%mvn_package org.mongodb:%{pkg_name}:* %{pkg_name}
%mvn_package org.mongodb:mongodb-driver-core:* %{pkg_name}-driver-core
%mvn_package org.mongodb:mongodb-driver-async:* %{pkg_name}-driver-async
%mvn_package org.mongodb:mongodb-driver:* %{pkg_name}-driver
%mvn_package org.mongodb:mongodb-javadoc-utils:* __noinstall
%mvn_file org.mongodb:bson:* %{pkg_name}/bson
%mvn_file org.mongodb:%{pkg_name}:* %{pkg_name}/mongo
%mvn_file org.mongodb:mongodb-driver-core:* %{pkg_name}/driver-core
%mvn_file org.mongodb:mongodb-driver-async:* %{pkg_name}/driver-async
%mvn_file org.mongodb:mongodb-driver:* %{pkg_name}/driver
%{?scl:EOF}


%build
%{?scl:scl enable %{buildscls} - << "EOF"}
set -ex
export MAVEN_OPTS="-Xmx2048m"
# not very nice hack needed in RHEL6
export JAVA_HOME="/usr/lib/jvm/java-1.8.0"
%mvn_build -- -Dproject.build.sourceEncoding=UTF-8
%{?scl:EOF}

%install
%{?scl:scl enable %{buildscls} - << "EOF"}
set -ex
%mvn_install
%{?scl:EOF}

%files -f .mfiles-%{pkg_name} -f .mfiles
%doc README.md LICENSE.txt

%files bson -f .mfiles-%{pkg_name}-bson
%doc README.md LICENSE.txt
%dir %{_datadir}/java/mongo-java-driver
%dir %{_datadir}/maven-metadata
%dir %{_datadir}/maven-poms/mongo-java-driver

%files driver -f .mfiles-%{pkg_name}-driver
%doc README.md LICENSE.txt

%files driver-core -f .mfiles-%{pkg_name}-driver-core
%doc README.md LICENSE.txt

%files driver-async -f .mfiles-%{pkg_name}-driver-async

%files javadoc -f .mfiles-javadoc
%doc README.md LICENSE.txt


%changelog
* Mon Oct 02 2017 Marek Skalický <mskalick@redhat.com> - 3.5.0-3
- Fix directory ownership
  Resolves: RHBZ#1466860

* Fri Sep 22 2017 Marek Skalický <mskalick@redhat.com> - 3.5.0-2
- Update to latest upstream version
  Resolves: RHBZ#1466860

* Mon Jul 03 2017 Tomas Repik <trepik@redhat.com> - 3.4.2-1
- Update to 3.4.2
  Resolves: RHBZ#1466860

* Tue Mar 29 2016 Severin Gehwolf <sgehwolf@redhat.com> - 3.2.1-3
- Add basic OSGi metadata.

* Thu Feb 18 2016 Marek Skalicky <mskalick@redhat.com> - 3.2.1-2
- Fixed directory ownership

* Tue Feb 2 2016 Marek Skalicky <mskalick@redhat.com> - 3.2.1-1
- Upgrade to 3.2.1 release (from Fedora 24)

* Mon Jul 27 2015 Severin Gehwolf <sgehwolf@redhat.com> - 2.13.2-5
- Fix bugs in SCL-ization. Most importantly, pkg name prefix.

* Mon Jul 27 2015 Severin Gehwolf <sgehwolf@redhat.com> - 2.13.2-4
- SCL-ize package.

* Mon Jun 22 2015 Omair Majid <omajid@redhat.com> - 2.13.2-3
- Require javapackages-tools, not jpackage-utils.

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.13.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Wed Jun 10 2015 Severin Gehwolf <sgehwolf@redhat.com> - 2.13.2-1
- Update to lastest upstream version.
- Resolves RHBZ#1178257.

* Tue Jun 10 2014 Severin Gehwolf <sgehwolf@redhat.com> - 2.11.3-4
- Fix FTBFS. Resolves RHBZ#1106228.
- Fix @VERSION@ substitution. Resolves RHBZ#1048200.

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.11.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Fri Mar 28 2014 Michael Simacek <msimacek@redhat.com> - 2.11.3-2
- Use Requires: java-headless rebuild (#1067528)

* Tue Sep 24 2013 Severin Gehwolf <sgehwolf@redhat.com> - 2.11.3-1
- Update to latest upstream release.

* Thu Sep 05 2013 Omair Majid <omajid@redhat.com> - 2.11.2-2
- Do not require -bson subpackage. The classes are present in both jars.

* Fri Aug 30 2013 Omair Majid <omajid@redhat.com> - 2.11.2-1
- Update to 2.11.2
- Generate tarball from commit tag, according to packaging guidelines

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.7.3-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.7.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Fri Jul 20 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.7.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Tue Apr 24 2012 Jon VanAlten <jon.vanalten@redhat.com> 2.7.3-1
- Bump to 2.7.3.

* Mon Jan 16 2012 Alexander Kurtakov <akurtako@redhat.com> 2.6.5-4
- Add depmap/pom.

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.6.5-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Nov 29 2011 Jon VanAlten <jon.vanalten@redhat.com> - 2.6.5-2
- Sources moved to lookaside cache where they belong

* Tue Nov 29 2011 Jon VanAlten <jon.vanalten@redhat.com> - 2.6.5-1
- Add missing BuildDep: git (git-hash is used during build)

* Tue Oct 11 2011 Jon VanAlten <jon.vanalten@redhat.com> - 2.6.5-1
- Initial packaging of mongo-java-driver for Fedora.
