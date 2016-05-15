%{?scl:%scl_package mongo-java-driver}
%{!?scl:%global pkg_name %{name}}

# Use java common's requires/provides generator
%{?java_common_find_provides_and_requires}

Name:		%{?scl_prefix}mongo-java-driver
Version:	2.14.1
Release:	1%{?dist}
Summary:	A Java driver for MongoDB

Group:		Development/Libraries
BuildArch:	noarch
License:	ASL 2.0
URL:		http://www.mongodb.org/display/DOCS/Java+Language+Center
Source0:	https://github.com/mongodb/%{pkg_name}/archive/r%{version}.tar.gz

BuildRequires:	rh-java-common-javapackages-tools
BuildRequires:	rh-java-common-javapackages-local
BuildRequires:	rh-java-common-maven-local
BuildRequires:	maven30-testng
BuildRequires:	rh-java-common-ant
BuildRequires:	maven30-ant-contrib
BuildRequires:	git

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

%package javadoc
Summary:	Javadoc for %{name}
Group:		Documentation

%description javadoc
This package contains the API documentation for %{name}.

%package bson-javadoc
Summary:	Javadoc for %{name}-bson
Group:		Documentation

%description bson-javadoc
This package contains the API documentation for %{name}-bson.

%prep
%{?scl:scl enable maven30 %{scl} - << "EOF"}
%setup -qn %{pkg_name}-r%{version}

find -name '*.class' -exec rm -f '{}' \;
find -name '*.jar' -exec rm -f '{}' \;
sed -i -e "s|@VERSION@|%{version}|g" maven/maven-bson.xml maven/maven-mongo-java-driver.xml
set -ex
%mvn_package org.mongodb:bson:* %{pkg_name}-bson
%mvn_package org.mongodb:%{pkg_name}:* %{pkg_name}
%mvn_file org.mongodb:bson:* %{pkg_name}/bson
%mvn_file org.mongodb:%{pkg_name}:* %{pkg_name}/mongo
%{?scl:EOF}

%build
%{?scl:scl enable maven30 %{scl} - << "EOF"}
(
  ln -s $(build-classpath testng) lib/testng-6.3.1.jar
  ant -Dfile.encoding=UTF-8 -Denv.JAVA_HOME=/usr/lib/jvm/java -Dplatforms.JDK_1.5.home=/usr/lib/jvm/java jar javadocs
)
%mvn_artifact maven/maven-bson.xml bson.jar
%mvn_artifact maven/maven-mongo-java-driver.xml mongo.jar
%{?scl:EOF}

%install
%{?scl:scl enable maven30 %{scl} - << "EOF"}
%mvn_install
# Java-docs
install -d -m 755                 %{buildroot}%{_javadocdir}/%{name}
install -d -m 755                 %{buildroot}%{_javadocdir}/%{name}-bson
cp -r -p docs/mongo-java-driver/* %{buildroot}%{_javadocdir}/%{name}
cp -r -p docs/bson/*              %{buildroot}%{_javadocdir}/%{name}-bson
%{?scl:EOF}

%files -f .mfiles-%{pkg_name}
%dir %{_javadir}/%{pkg_name}
%dir %{_mavenpomdir}/%{pkg_name}
%dir %{_datadir}/maven-metadata
%doc README.md LICENSE.txt

%files bson -f .mfiles-%{pkg_name}-bson
%dir %{_javadir}/%{pkg_name}
%dir %{_mavenpomdir}/%{pkg_name}
%dir %{_datadir}/maven-metadata
%doc README.md LICENSE.txt

%files javadoc
%{_javadocdir}/%{name}
%doc README.md LICENSE.txt

%files bson-javadoc
%{_javadocdir}/%{name}-bson
%doc README.md LICENSE.txt

%changelog
* Tue Feb 2 2016 Marek Skalicky <mskalick@redhat.com> - 2.14.1-1
- Upgrade to latest compatible release 2.14.1
  Resolves: RHBZ#1247166

* Thu Mar 19 2015 Marek Skalicky <mskalick@redhat.com> - 2.11.4-7
- Fixed maven-metadata ownership

* Wed Jan 21 2015 Michal Srb <msrb@redhat.com> - 2.11.4-6
- Remove exlicit requires
- Fix directory ownership

* Tue Jan 20 2015 Severin Gehwolf <sgehwolf@redhat.com> - 2.11.4-5
- Make package buildable with xmvn 2.2.x.
- Use java common's requires/provides generators.

* Tue Jun 24 2014 Honza Horak <hhorak@redhat.com> - 2.11.4-4
- Return java requirements
  Related: #1110884

* Wed Jun 18 2014 Severin Gehwolf <sgehwolf@redhat.com> 2.11.4-3
- Build using maven30 collection.

* Fri Mar 28 2014 Jan Pacner <jpacner@redhat.com> - 2.11.4-2
- Resolves: #1075025 (Leftovers files after mongodb packages removal)

* Wed Jan 29 2014 Jan Pacner <jpacner@redhat.com> - 2.11.4-1
- Resolves: #1059170 (new release 2.11.4)

* Fri Jan 10 2014 Jan Pacner <jpacner@redhat.com> - 2.11.3-8
- Related: RHBZ#1046029; unify el6 and el7 branch

* Tue Jan 07 2014 Honza Horak <hhorak@redhat.com> 2.11.3-7
- Filter properly in RHEL-6 and lower
  Related: RHBZ#1046029

* Fri Jan 03 2014 Severin Gehwolf <sgehwolf@redhat.com> 2.11.3-6
- Don't generate osgi() style provides.
- Resolves: RHBZ#1046029.

* Thu Nov 14 2013 Severin Gehwolf <sgehwolf@redhat.com> - 2.11.3-5
- Fix auto-requires/provides.

* Thu Nov 14 2013 Severin Gehwolf <sgehwolf@redhat.com> - 2.11.3-4
- Disable macro for auto-requires/provides.
- Fix bson maven provides.
- Expand @VERSION@ in poms.

* Wed Nov 13 2013 Severin Gehwolf <sgehwolf@redhat.com> - 2.11.3-3
- Remove unneeded testng BR.
- Make package build with ant-contrib (custom classpath)
- Don't use maven* macros.

* Thu Oct  3 2013 Honza Horak <hhorak@redhat.com> - 2.11.3-2
- Port to SCL

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
