%{?scl:%scl_package mongo-java-driver}
%{!?scl:%global pkg_name %{name}}

# Exclude generation of osgi() style provides, since they are not
# SCL-namespaced and may conflict with base RHEL packages.
# See: https://bugzilla.redhat.com/show_bug.cgi?id=1046029
%if 0%{?rhel} < 7
# get proper auto provides/requires
%{?scl: %mongodb24_find_provides_and_requires}
%filter_from_provides /^osgi(.*)$/d
%else
%global __provides_exclude ^osgi(.*)$
%endif

Name:		%{?scl_prefix}mongo-java-driver
Version:	2.11.4
Release:	4%{?dist}
Summary:	A Java driver for MongoDB

Group:		Development/Libraries
BuildArch:	noarch
License:	ASL 2.0
URL:		http://www.mongodb.org/display/DOCS/Java+Language+Center
Source0:	https://github.com/mongodb/%{pkg_name}/archive/r%{version}.tar.gz

BuildRequires:	rh-java-common-javapackages-tools
BuildRequires:	rh-java-common-maven-local
BuildRequires:	rh-java-common-ant-apache-regexp
BuildRequires:	maven30-testng
BuildRequires:	rh-java-common-ant
BuildRequires:	maven30-ant-contrib
BuildRequires:	git

Requires:	jpackage-utils
Requires:	java
%{?scl:Requires:%scl_runtime}

%description
This is the Java driver for MongoDB.

%package bson
Summary:	A Java-based BSON implementation
Group:		Development/Libraries
Requires:	jpackage-utils
Requires:	java
%{?scl:Requires:%scl_runtime}

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
Requires:	jpackage-utils
%{?scl:Requires:%scl_runtime}

%description javadoc
This package contains the API documentation for %{name}.

%package bson-javadoc
Summary:	Javadoc for %{name}-bson
Group:		Documentation
Requires:	jpackage-utils
%{?scl:Requires:%scl_runtime}

%description bson-javadoc
This package contains the API documentation for %{name}-bson.

%prep
%setup -qn %{pkg_name}-r%{version}

find -name '*.class' -exec rm -f '{}' \;
find -name '*.jar' -exec rm -f '{}' \;

%build
%{?scl:scl enable maven30 %{scl} - << "EOF"}
(
  ln -s $(build-classpath testng) lib/testng-6.3.1.jar
  ant -Dfile.encoding=UTF-8 -Denv.JAVA_HOME=/usr/lib/jvm/java -Dplatforms.JDK_1.5.home=/usr/lib/jvm/java jar javadocs
)
sed -i -e "s|@VERSION@|%{version}|g" maven/maven-bson.xml maven/maven-mongo-java-driver.xml
%{?scl:EOF}

%install
%{?scl:scl enable maven30 %{scl} - << "EOF"}
# Jars
install -d -m 755       %{buildroot}%{_javadir}
install -p -m 644 *.jar %{buildroot}%{_javadir}/

# poms
install -d -m 755 %{buildroot}%{_datadir}/maven-poms
install -Dpm 644 maven/maven-mongo-java-driver.xml %{buildroot}%{_mavenpomdir}/JPP-mongo.pom
install -Dpm 644 maven/maven-bson.xml              %{buildroot}%{_mavenpomdir}/JPP-bson.pom
%add_maven_depmap JPP-mongo.pom mongo.jar
%add_maven_depmap -f bson JPP-bson.pom bson.jar

# Java-docs
install -d -m 755                 %{buildroot}%{_javadocdir}/%{name}
install -d -m 755                 %{buildroot}%{_javadocdir}/%{name}-bson
cp -r -p docs/mongo-java-driver/* %{buildroot}%{_javadocdir}/%{name}
cp -r -p docs/bson/*              %{buildroot}%{_javadocdir}/%{name}-bson
%{?scl:EOF}

%files
%{_javadir}/mongo.jar
%doc README.md LICENSE.txt
%{_mavenpomdir}/JPP-mongo.pom
%{_datadir}/maven-metadata/%{pkg_name}.xml

%files bson
%{_javadir}/bson.jar
%doc README.md LICENSE.txt
%{_mavenpomdir}/JPP-bson.pom
%{_datadir}/maven-metadata/%{pkg_name}-bson.xml

%files javadoc
%{_javadocdir}/%{name}
%doc README.md LICENSE.txt

%files bson-javadoc
%{_javadocdir}/%{name}-bson
%doc README.md LICENSE.txt

%changelog
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
