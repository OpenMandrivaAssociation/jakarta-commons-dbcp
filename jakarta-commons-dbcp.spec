# Copyright (c) 2000-2007, JPackage Project
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
# 3. Neither the name of the JPackage Project nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

%define _with_gcj_support 1
%define _without_maven 1

%define gcj_support %{?_with_gcj_support:1}%{!?_with_gcj_support:%{?_without_gcj_support:0}%{!?_without_gcj_support:%{?_gcj_support:%{_gcj_support}}%{!?_gcj_support:0}}}

# If you don't want to build with maven, and use straight ant instead,
# give rpmbuild option '--without maven'

%define with_maven %{!?_without_maven:1}%{?_without_maven:0}
%define without_maven %{?_without_maven:1}%{!?_without_maven:0}

%define base_name       dbcp
%define short_name      commons-%{base_name}
%define section         free

Name:           jakarta-commons-dbcp
Version:        1.2.2
Release:        %mkrel 1.0.2
Epoch:          0
Summary:        Jakarta Commons DataBase Pooling Package
License:        Apache Software License 
Group:          Development/Java
Source0:        http://archive.apache.org/dist/jakarta/commons/dbcp/source/%{short_name}-%{version}-src.tar.gz 
Source1:        pom-maven2jpp-depcat.xsl
Source2:        pom-maven2jpp-newdepmap.xsl
Source3:        pom-maven2jpp-mapdeps.xsl
Source4:        %{base_name}-%{version}-jpp-depmap.xml
Source5:        commons-build.tar.gz
# svn export -r '{2007-02-15}' http://svn.apache.org/repos/asf/jakarta/commons/proper/commons-build/trunk/ commons-build
# tar czf commons-build.tar.gz commons-build
Source6:        dbcp-tomcat5-build.xml
Source7:        commons-dbcp-1.2.2.pom

Patch0:         commons-dbcp-1.2.2-project_xml.patch

Url:            http://jakarta.apache.org/commons/%{base_name}
BuildRequires:  ant
BuildRequires:  jakarta-commons-collections >= 2.0
BuildRequires:  jakarta-commons-pool >= 1.3
BuildRequires:  jakarta-commons-logging >= 1.1
BuildRequires:  jdbc-stdext >= 2.0
BuildRequires:  xerces-j2
BuildRequires:  xml-commons-apis >= 0:1.3
BuildRequires:  java-rpmbuild > 1.7.2
BuildRequires:  junit >= 3.8.1
BuildRequires:  jakarta-commons-pool-tomcat5
BuildRequires:  jakarta-commons-collections-tomcat5
BuildRequires:  tomcat5-common-lib
%if %{with_maven}
BuildRequires:  maven >= 0:1.1
BuildRequires:  maven-plugins-base
BuildRequires:  maven-plugin-artifact
BuildRequires:  maven-plugin-checkstyle
BuildRequires:  sf-cobertura-maven-plugin
BuildRequires:  sf-findbugs-maven-plugin
BuildRequires:  maven-plugin-pmd
BuildRequires:  maven-plugin-xdoc
BuildRequires:  maven-plugin-test
BuildRequires:  maven-plugin-license
BuildRequires:  maven-plugin-changes
BuildRequires:  saxon
BuildRequires:  saxon-scripts
%endif


Requires:       update-alternatives
Requires(post): update-alternatives
Requires(preun):  update-alternatives
Requires:       jakarta-commons-collections >= 2.0
Requires:       jakarta-commons-pool >= 1.1
%if ! %{gcj_support}
BuildArch:      noarch
%endif

BuildRoot:  %{_tmppath}/%{name}-buildroot
Provides:   %{short_name} = %{epoch}:%{version}-%{release}
Provides:   hibernate_jdbc_cache = %{epoch}:%{version}-%{release}
Obsoletes:  %{short_name} < %{epoch}:%{version}-%{release}

%if %{gcj_support}
BuildRequires:          java-gcj-compat-devel
%endif

%description
Many Jakarta projects support interaction with a relational 
database. Creating a new connection for each user can be time 
consuming (often requiring multiple seconds of clock time), 
in order to perform a database transaction that might take 
milliseconds. Opening a connection per user can be unfeasible 
in a publicly-hosted Internet application where the number of 
simultaneous users can be very large. Accordingly, developers 
often wish to share a "pool" of open connections between all 
of the application's current users. The number of users actually 
performing a request at any given time is usually a very small 
percentage of the total number of active users, and during 
request processing is the only time that a database connection 
is required. The application itself logs into the DBMS, and 
handles any user account issues internally.

%package javadoc
Summary:        Javadoc for %{name}
Group:          Development/Java
Requires(post):   /bin/rm,/bin/ln
Requires(postun): /bin/rm

%description javadoc
Javadoc for %{name}.

%package tomcat5
Summary:        DBCP dependency for Tomcat5
Group:          Development/Java


%description tomcat5
DBCP dependency for Tomcat5

%if %{with_maven}
%package manual
Summary:        Documents for %{name}
Group:          Development/Java

%description manual
%{summary}.
%endif

%prep

%setup -q -n %{short_name}-%{version}-src
# quick hack
cp LICENSE.txt ../LICENSE
# remove all binary libs
find . -name "*.jar" -exec rm -f {} \;
gzip -dc %{SOURCE5} | tar xf -
cp %{SOURCE6} .

%patch0 -b .sav

%build
%if %{with_maven}
export DEPCAT=$(pwd)/%{base_name}-%{version}-depcat.new.xml
echo '<?xml version="1.0" standalone="yes"?>' > $DEPCAT
echo '<depset>' >> $DEPCAT
for p in $(find . -name project.xml); do
    pushd $(dirname $p)
    /usr/bin/saxon project.xml %{SOURCE1} >> $DEPCAT
    popd
done
echo >> $DEPCAT
echo '</depset>' >> $DEPCAT
/usr/bin/saxon $DEPCAT %{SOURCE2} > %{base_name}-%{version}-depmap.new.xml

for p in $(find . -name project.xml); do
    pushd $(dirname $p)
    cp project.xml project.xml.orig
    /usr/bin/saxon -o project.xml project.xml.orig %{SOURCE3} map=%{SOURCE4}
    popd
done
mkdir -p .maven/repository/JPP/jars
pushd .maven/repository/JPP/jars
    ln -sf $(build-classpath jdbc-stdext) jdbc.jar
popd

maven \
        -Dmaven.repo.remote=file:/usr/share/maven/repository \
        -Dmaven.home.local=$(pwd)/.maven \
        jar javadoc xdoc:transform
%else

export CLASSPATH=$(build-classpath jdbc-stdext xerces-j2)
%ant \
        -Dcommons-pool.jar=$(build-classpath commons-pool) \
        -Djdbc20ext.jar=$(build-classpath jdbc-stdext) \
        -Djunit.jar=$(build-classpath junit) \
        -Dxerces.jar=$(build-classpath xerces-j2) \
        -Dxml-apis.jar=$(build-classpath xml-commons-jaxp-1.3-apis) \
        -Dnaming-common.jar=$(build-classpath tomcat5/naming-resources) \
        -Dnaming-java.jar=$(build-classpath tomcat5/naming-factory) \
        -Dlogging.jar=$(build-classpath commons-logging) \
        -Djava.io.tmpdir=. \
        dist test
%endif

export CLASSPATH=$(build-classpath jdbc-stdext xerces-j2 commons-collections-tomcat5 commons-pool-tomcat5)        
%ant     -f dbcp-tomcat5-build.xml

%install
rm -rf $RPM_BUILD_ROOT
# jars
install -d -m 755 $RPM_BUILD_ROOT%{_javadir}
%if %{with_maven}
install -m 644 target/%{short_name}-%{version}.jar $RPM_BUILD_ROOT%{_javadir}/%{name}-%{version}.jar
%else
install -m 644 dist/%{short_name}.jar $RPM_BUILD_ROOT%{_javadir}/%{name}-%{version}.jar
%endif
#tomcat5 jars 
install -m 644 dbcp-tomcat5/%{short_name}-tomcat5.jar $RPM_BUILD_ROOT%{_javadir}/%{name}-tomcat5-%{version}.jar

(cd $RPM_BUILD_ROOT%{_javadir} && for jar in *-%{version}*; do ln -sf ${jar} `echo $jar| sed  "s|jakarta-||g"`; done)
(cd $RPM_BUILD_ROOT%{_javadir} && for jar in *-%{version}*; do ln -sf ${jar} `echo $jar| sed  "s|-%{version}||g"`; done)

%add_to_maven_depmap commons-dbcp commons-dbcp %{version} JPP %{name}

# pom
install -d -m 755 $RPM_BUILD_ROOT%{_datadir}/maven2/poms
install -pm 644 %{SOURCE7} \
    $RPM_BUILD_ROOT%{_datadir}/maven2/poms/JPP-%{name}.pom


# javadoc
install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
%if %{with_maven}
cp -pr target/docs/apidocs/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
rm -rf target/docs/apidocs
%else
cp -pr dist/docs/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
%endif
ln -s %{name}-%{version} $RPM_BUILD_ROOT%{_javadocdir}/%{name}

%if %{with_maven}
# manual
install -d -m 755 $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}
cp -pr target/docs/* $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}
%endif

# quick hack clean up
rm ../LICENSE

# hibernate_jdbc_cache ghost symlink
ln -s %{_sysconfdir}/alternatives/hibernate_jdbc_cache \
  $RPM_BUILD_ROOT%{_javadir}/hibernate_jdbc_cache.jar

%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post
update-alternatives --install %{_javadir}/hibernate_jdbc_cache.jar \
  hibernate_jdbc_cache %{_javadir}/%{name}.jar 60
%update_maven_depmap
%if %{gcj_support}
%{update_gcjdb}
%endif


%postun
%update_maven_depmap
%if %{gcj_support}
%{clean_gcjdb}
%endif
# (anssi) cleaned up a bit:
if [ $1 -eq 0 ] || ! [ -e %{_javadir}/%{name}.jar ]; then
  update-alternatives --remove hibernate_jdbc_cache %{_javadir}/%{name}.jar
fi

%if %{gcj_support}
%post tomcat5
%{update_gcjdb}
%endif

%if %{gcj_support}
%postun tomcat5
%{clean_gcjdb}
%endif

%files
%defattr(-,root,root)
%doc LICENSE.txt NOTICE.txt README.txt
%{_javadir}/%{name}.jar
%{_javadir}/%{name}-%{version}.jar
%{_javadir}/%{short_name}.jar
%{_javadir}/%{short_name}-%{version}.jar
%ghost %{_javadir}/hibernate_jdbc_cache.jar
%{_datadir}/maven2/poms/*
%{_mavendepmapfragdir}
%if %{gcj_support}
# (anssi) own the directory:
%dir %{_libdir}/gcj/%{name}
%attr(-,root,root) %{_libdir}/gcj/%{name}/%{name}-%{version}.jar.*
%endif

%files tomcat5
%defattr(-,root,root)
%{_javadir}/*-tomcat5*.jar
%doc LICENSE.txt NOTICE.txt

%if %{gcj_support}
# (anssi) own the directory:
%dir %{_libdir}/gcj/%{name}
%attr(-,root,root) %{_libdir}/gcj/%{name}/*-tomcat5*
%endif

%files javadoc
%defattr(-,root,root)
%doc %{_javadocdir}/%{name}-%{version}
%doc %{_javadocdir}/%{name}

%if %{with_maven}
%files manual
%defattr(0644,root,root,0755)
%doc %{_docdir}/%{name}-%{version}
%endif

