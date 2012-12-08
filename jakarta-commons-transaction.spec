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
%define gcj_support %{?_with_gcj_support:1}%{!?_with_gcj_support:%{?_without_gcj_support:0}%{!?_without_gcj_support:%{?_gcj_support:%{_gcj_support}}%{!?_gcj_support:0}}}

# If you don't want to build with maven, and use straight ant instead,
# give rpmbuild option '--without maven'
%define _without_maven 1

%define with_maven %{!?_without_maven:1}%{?_without_maven:0}
%define without_maven %{?_without_maven:1}%{!?_without_maven:0}

%define section   free
%define base_name commons-transaction

Name:           jakarta-commons-transaction
Version:        1.1
Release:        7.0.6
Epoch:          0
Summary:        Commons Transaction
License:        Apache License 2.0
Url:            http://jakarta.apache.org/commons/transaction/
Group:          Development/Java
Source0:        commons-transaction-1.1-src.tgz

Source1:        pom-maven2jpp-depcat.xsl
Source2:        pom-maven2jpp-newdepmap.xsl
Source3:        pom-maven2jpp-mapdeps.xsl
Source4:        commons-transaction-1.1-jpp-depmap.xml

Source10:	%{name}.rpmlintrc

Patch0:         commons-transaction-1.1-project_xml.patch

Requires:       jakarta-commons-codec
Requires:       geronimo-jta-1.0.1B-api
Requires:       log4j
Requires:       xerces-j2
Requires:       xml-commons-apis
BuildRequires:  java-rpmbuild
BuildRequires:  jpackage-utils >= 0:1.7
BuildRequires:  ant >= 0:1.6
%if %{with_maven}
BuildRequires:  maven >= 0:1.0.2
BuildRequires:  maven-plugins-base
BuildRequires:  maven-plugin-test
BuildRequires:  maven-plugin-xdoc
BuildRequires:  maven-plugin-license
BuildRequires:  saxon
BuildRequires:  saxon-scripts
%endif
BuildRequires:  junit
BuildRequires:  jakarta-commons-beanutils
BuildRequires:  jakarta-commons-codec
BuildRequires:  geronimo-jta-1.0.1B-api
BuildRequires:  log4j
BuildRequires:  xerces-j2
BuildRequires:  xml-commons-apis
%if ! %{gcj_support}
BuildArch:      noarch
%endif
BuildRoot:      %{_tmppath}/%{name}-%{version}-buildroot
%if %{gcj_support}
BuildRequires:          java-gcj-compat-devel
%endif

%description
Commons Transaction aims at providing lightweight, 
standardized, well tested and efficient implementations 
of utility classes commonly used in transactional Java 
programming. Initially there are implementations for 
multi level locks, transactional collections and 
transactional file access. There may be additional 
implementations when the common need for them becomes 
obvious. However, the complete component shall remain 
compatible to JDK1.2 and should have minimal dependencies.

%package javadoc
Summary:        Javadoc for %{name}
Group:          Development/Java
Requires(post): /bin/rm /bin/ln
Requires(postun): /bin/rm

%description javadoc
%{summary}.

%prep
%setup -q -c -n %{base_name}
%remove_java_binaries

%if %{with_maven}
export DEPCAT=$(pwd)/commons-transaction-1.1-depcat.new.xml
echo '<?xml version="1.0" standalone="yes"?>' > $DEPCAT
echo '<depset>' >> $DEPCAT
for p in $(find . -name project.xml); do
    pushd $(dirname $p)
    /usr/bin/saxon project.xml %{SOURCE1} >> $DEPCAT
    popd
done
echo >> $DEPCAT
echo '</depset>' >> $DEPCAT
/usr/bin/saxon $DEPCAT %{SOURCE2} > commons-transaction-1.1-depmap.new.xml
%endif

%patch0 -b .sav

%build
%if %{with_maven}
for p in $(find . -name project.xml); do
    pushd $(dirname $p)
    cp project.xml project.xml.orig
    /usr/bin/saxon -o project.xml project.xml.orig %{SOURCE3} map=%{SOURCE4}
    popd
done

maven -Dmaven.repo.remote=file:/usr/share/maven/repository \
      -Dmaven.javadoc.source=1.4 \
      -Dmaven.home.local=$(pwd)/.maven \
      jar javadoc 
%else
export CLASSPATH=$(build-classpath ant ant-launcher log4j jta commons-codec):build/classes
%{ant} -Dbuild.sysclasspath=only jar javadocs
%endif

%install
rm -rf $RPM_BUILD_ROOT
# jars
install -d -m 755 $RPM_BUILD_ROOT%{_javadir}
%if %{with_maven}
install -m 644 target/commons-transaction-1.1.jar \
           $RPM_BUILD_ROOT%{_javadir}/%{name}-%{version}.jar
%else
install -m 644 build/lib/commons-transaction-1.1.jar \
           $RPM_BUILD_ROOT%{_javadir}/%{name}-%{version}.jar
%endif

(cd $RPM_BUILD_ROOT%{_javadir} && for jar in jakarta-*; do \
ln -sf ${jar} ${jar/jakarta-/}; done)
(cd $RPM_BUILD_ROOT%{_javadir} && for jar in *-%{version}*; do \
ln -sf ${jar} ${jar/-%{version}/}; done)

# javadoc
install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
%if %{with_maven}
cp -pr target/docs/apidocs/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
%else
cp -pr build/doc/apidocs/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
%endif
touch $RPM_BUILD_ROOT%{_javadocdir}/%{name} 
rm -rf target/docs/apidocs

## manual
install -d -m 755 $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}
cp -p LICENSE.txt $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}

%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%if %{gcj_support}
%post
%{update_gcjdb}
%endif

%if %{gcj_support}
%postun
%{clean_gcjdb}
%endif

%files
%defattr(0644,root,root,0755)
%{_docdir}/%{name}-%{version}/LICENSE.txt
%{_javadir}/*
%if %{gcj_support}
%dir %attr(-,root,root) %{_libdir}/gcj/%{name}
%attr(-,root,root) %{_libdir}/gcj/%{name}/%{name}-%{version}.jar.*
%endif

%files javadoc
%defattr(0644,root,root,0755)
%{_javadocdir}/%{name}-%{version}
%{_javadocdir}/%{name}


%changelog
* Fri Dec 03 2010 Oden Eriksson <oeriksson@mandriva.com> 0:1.1-7.0.4mdv2011.0
+ Revision: 606063
- rebuild

* Wed Mar 17 2010 Oden Eriksson <oeriksson@mandriva.com> 0:1.1-7.0.3mdv2010.1
+ Revision: 523006
- rebuilt for 2010.1

* Wed Sep 02 2009 Christophe Fergeau <cfergeau@mandriva.com> 0:1.1-7.0.2mdv2010.0
+ Revision: 425445
- rebuild

* Tue Jan 08 2008 Alexander Kurtakov <akurtakov@mandriva.org> 0:1.1-7.0.1mdv2008.1
+ Revision: 146514
- add log4j to ant classpath
- add java-rpmbuild BR
- another fix for ant classpath
- fix ant classpath
- import jakarta-commons-transaction


