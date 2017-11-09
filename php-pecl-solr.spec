#
# Conditional build:
%bcond_without	tests		# build without tests
%bcond_with	network_tests	# run tests requiring setup Solr Server on localhost:8983

%define		php_name	php%{?php_suffix}
%define		modname solr
Summary:	Object oriented API to Apache Solr
Summary(fr.UTF-8):	API orientée objet pour Apache Solr
Name:		%{php_name}-pecl-solr
Version:	2.4.0
Release:	1
License:	PHP v3.01
Group:		Development/Languages
Source0:	https://pecl.php.net/get/%{modname}-%{version}.tgz
# Source0-md5:	2c9accf66681a3daaaf371bc07e44902
Patch0:		tests-online.patch
URL:		https://pecl.php.net/package/solr
BuildRequires:	%{php_name}-cli
BuildRequires:	%{php_name}-devel >= 4:5.3.0
BuildRequires:	curl-devel
BuildRequires:	libxml2-devel >= 1:2.6.16
BuildRequires:	php-packagexml2cl
BuildRequires:	rpmbuild(macros) >= 1.666
%if %{with tests}
BuildRequires:	%{php_name}-curl
BuildRequires:	%{php_name}-json
BuildRequires:	%{php_name}-pcre
BuildRequires:	%{php_name}-xml
%endif
%{?requires_php_extension}
Requires:	%{php_name}-cli
Requires:	%{php_name}-json
Requires:	%{php_name}-pcre
Requires:	%{php_name}-xml
Provides:	php(solr) = %{version}
Obsoletes:	php-pecl-solr < 1.0.2-6
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Feature-rich library that allows PHP developers to communicate easily
and efficiently with Apache Solr server instances using an
object-oriented API.

It effectively simplifies the process of interacting with Apache Solr
using PHP5 and it already comes with built-in readiness for the latest
features available in Solr 1.4. The extension has features such as
built-in, serializable query string builder objects which effectively
simplifies the manipulation of name-value pair request parameters
across repeated requests. The response from the Solr server is also
automatically parsed into native php objects whose properties can be
accessed as array keys or object properties without any additional
configuration on the client-side. Its advanced HTTP client reuses the
same connection across multiple requests and provides built-in support
for connecting to Solr servers secured behind HTTP Authentication or
HTTP proxy servers. It is also able to connect to SSL-enabled
containers.

Notice: PECL Solr 2.x is not compatible with Apache Solr Server 3.x

%description -l fr.UTF-8
Bibliothèque riche en fonctionnalités qui permet aux développeurs PHP
de communiquer facilement et efficacement avec des instances du
serveur Apache Solr en utilisant une API orientée objet.

Cela simplifie réellement le processus d'interaction avec Apache Solr
en utilisant PHP5 et fournit dores et déjà des facilités pour les
dernières fonctionnalités disponibles dans Solr 1.4. L'extension
possède des fonctionnalités telles qu'un constructeur de requêtes
embarqué et sérialisable qui simplifie réellement la manipulation des
couples de paramètres nom-valeur entre différentes requêtes. La
réponse de Solr est également analysée automatiquement en objets php
natifs dont les propriétés sont accessibles en tant que clés de
tableaux ou en tant que propriétés d'objets sans la moindre
configuration supplémentaire sur le client. Son client HTTP avancé
utilise la même connexion entre différentes requêtes et fournit un
support embarqué pour la connexion aux serveurs Solr protégés par
authentification HTTP ou par un serveur mandataire. Il est également
possible de se connecter à des serveurs via SSL.

%prep
%setup -qc
mv %{modname}-%{version}/* .
%{!?with_network_tests:%patch0 -p1}

cat <<'EOF' > run-tests.sh
#!/bin/sh
export NO_INTERACTION=1 REPORT_EXIT_STATUS=1 MALLOC_CHECK_=2
exec %{__make} test \
	PHP_EXECUTABLE=%{__php} \
	PHP_TEST_SHARED_SYSTEM_EXTENSIONS="json pcre" \
	RUN_TESTS_SETTINGS="-q $*"
EOF
chmod +x run-tests.sh

%build
packagexml2cl package.xml > ChangeLog

# Check version
extver=$(awk -F'"' '/define PHP_SOLR_VERSION / {print $2}' src/php%{php_major_version}/php_solr_version.h)
if test "x${extver}" != "x%{version}"; then
	: Error: Upstream version is ${extver}, expecting %{version}.
	exit 1
fi

phpize
%configure
%{__make}

%{__php} -n -q \
	-d extension_dir=modules \
	-d extension=%{php_extensiondir}/curl.so \
	-d extension=%{php_extensiondir}/json.so \
	-d extension=%{modname}.so \
	-m > modules.log
grep %{modname} modules.log

%if %{with tests}
./run-tests.sh --show-diff
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{php_sysconfdir}/conf.d,%{php_extensiondir}}
%{__make} install \
	EXTENSION_DIR=%{php_extensiondir} \
	INSTALL_ROOT=$RPM_BUILD_ROOT

cat <<'EOF' > $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d/%{modname}.ini
; Enable Solr extension module
extension=%{modname}.so
EOF

%clean
rm -rf $RPM_BUILD_ROOT

%post
%php_webserver_restart

%postun
if [ "$1" = 0 ]; then
	%php_webserver_restart
fi

%files
%defattr(644,root,root,755)
%doc ChangeLog CREDITS README.SUBMITTING_CONTRIBUTIONS README.MEMORY_ALLOCATION
%doc README.ABOUT_SOLR_EXTENSION TODO LICENSE docs/documentation.php
%config(noreplace) %verify(not md5 mtime size) %{php_sysconfdir}/conf.d/%{modname}.ini
%{php_extensiondir}/%{modname}.so
