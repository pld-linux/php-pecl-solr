#
# Conditional build:
%bcond_without	tests		# build without tests

%define		modname solr
Summary:	Object oriented API to Apache Solr
Summary(fr.UTF-8):	API orientée objet pour Apache Solr
Name:		php-pecl-solr
Version:	1.0.2
Release:	1
License:	PHP
Group:		Development/Languages
URL:		http://pecl.php.net/package/solr
Source0:	http://pecl.php.net/get/%{modname}-%{version}.tgz
# Source0-md5:	1632144b462ab22b91d03e4d59704fab
BuildRequires:	curl-devel
BuildRequires:	libxml2-devel >= 1:2.6.16
%{?with_tests:BuildRequires:	php-curl}
BuildRequires:	php-devel >= 4:5.2.3
BuildRequires:	php-packagexml2cl
BuildRequires:	rpmbuild(macros) >= 1.519
Requires:	php-xml
Provides:	php-solr = %{version}
%{?requires_php_extension}
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
%setup -q -c
mv %{modname}-%{version}/* .

# avoid 1970 dates in doc
find -newer TODO -o -print | xargs touch --reference %{SOURCE0}

%build
packagexml2cl package.xml > ChangeLog

phpize
%configure
%{__make}

%if %{with tests}
ln -sf %{php_extensiondir}/curl.so modules
%{_bindir}/php \
	-n -q -d extension_dir=modules \
	-d extension=curl.so \
	-d extension=%{modname}.so \
	--modules | grep %{modname}
rm -f modules/curl.so
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

%files
%defattr(644,root,root,755)
%doc ChangeLog CREDITS README.SUBMITTING_CONTRIBUTIONS README.MEMORY_ALLOCATION
%doc README.ABOUT_SOLR_EXTENSION TODO LICENSE docs/documentation.php
%config(noreplace) %verify(not md5 mtime size) %{php_sysconfdir}/conf.d/%{modname}.ini
%{php_extensiondir}/%{modname}.so
