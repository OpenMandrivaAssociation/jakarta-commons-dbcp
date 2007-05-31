%define base_name	dbcp
%define short_name	commons-%{base_name}
%define name		jakarta-%{short_name}
%define version		1.2.1
%define	section		devel
%define gcj_support	1

Name:		%{name}
Version:	%{version}
Release:	%mkrel 5.1
Epoch:		0
Summary:	Jakarta Commons DataBase Pooling Package
License:	Apache License
Group:		Development/Java
#Vendor:		JPackage Project
#Distribution:	JPackage
Source0:	http://www.apache.org/dist/jakarta/commons/dbcp/source/%{short_name}-%{version}-src-MDVCLEAN.tar.bz2
Url:		http://jakarta.apache.org/commons/%{base_name}
BuildRequires:	ant
BuildRequires:	jakarta-commons-collections >= 0:2.0
BuildRequires:	jakarta-commons-pool >= 0:1.1
BuildRequires:	jdbc-stdext >= 0:2.0
BuildRequires:	xml-commons-apis
BuildRequires:  jpackage-utils > 0:1.5
BuildRequires:	junit >= 0:3.7
Requires:	/usr/sbin/update-alternatives
Requires:	jakarta-commons-collections >= 0:2.0
Requires:	jakarta-commons-pool >= 0:1.1
%if %{gcj_support}
BuildRequires:    java-gcj-compat-devel
Requires(post):   java-gcj-compat
Requires(postun): java-gcj-compat
%else
BuildArch:      noarch
%endif
BuildRoot:	%{_tmppath}/%{name}-%{version}-buildroot
Provides:	%{short_name}
Provides:	hibernate_jdbc_cache
Obsoletes:	%{short_name}

%description
The DBCP package shall create and maintain a database connection pool
package written in the Java language to be distributed under the ASF
license. The package shall be available as a pseudo-JDBC driver and
via a DataSource interface. The package shall also support multiple
logins to multiple database systems, reclamation of stale or dead
connections, testing for valid connections, PreparedStatement
pooling, and other features.

%package javadoc
Summary:	Javadoc for %{name}
Group:		Development/Java

%description javadoc
Javadoc for %{name}.

%prep
%setup -q -n %{short_name}-%{version}
# quick hack
cp LICENSE.txt ../LICENSE
# remove all binary libs
find . -name "*.jar" -exec rm -f {} \;

%build
export CLASSPATH=$(build-classpath commons-collections commons-pool jdbc-stdext junit)
%ant -Djava.io.tmpdir=. dist

%install
# jars
install -d -m 755 $RPM_BUILD_ROOT%{_javadir}
install -m 644 dist/%{short_name}.jar $RPM_BUILD_ROOT%{_javadir}/%{name}-%{version}.jar
(cd $RPM_BUILD_ROOT%{_javadir} && for jar in *-%{version}*; do ln -sf ${jar} `echo $jar| sed  "s|jakarta-||g"`; done)
(cd $RPM_BUILD_ROOT%{_javadir} && for jar in *-%{version}*; do ln -sf ${jar} `echo $jar| sed  "s|-%{version}||g"`; done)
# javadoc
install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
cp -pr dist/docs/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}

%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

# quick hack clean up
rm ../LICENSE

# hibernate_jdbc_cache ghost symlink
ln -s %{_sysconfdir}/alternatives \
  $RPM_BUILD_ROOT%{_javadir}/hibernate_jdbc_cache.jar

%{__perl} -pi -e 's/\r\n/\n/g' *.txt


%clean
rm -rf $RPM_BUILD_ROOT

%post
update-alternatives --install %{_javadir}/hibernate_jdbc_cache.jar \
  hibernate_jdbc_cache %{_javadir}/%{name}.jar 60
%if %{gcj_support}
%{update_gcjdb}

%postun
%{clean_gcjdb}
%endif

%preun
{
  [ $1 -eq 0 ] || exit 0
  update-alternatives --remove hibernate_jdbc_cache %{_javadir}/%{name}.jar
} >/dev/null 2>&1 || :

%files
%defattr(-,root,root)
%doc LICENSE.txt
%{_javadir}/*
%if %{gcj_support}
%attr(-,root,root) %{_libdir}/gcj/%{name}
%endif
%ghost %{_javadir}/hibernate_jdbc_cache.jar

%files javadoc
%defattr(-,root,root)
%{_javadocdir}/%{name}-%{version}
