# Author : George Tzoumas <geotz[at]gmail[dot]com>
# Maintainer: Nick Kavalieris <ph4ntome[at]gmail[dot]com>
# For contributors check the AUTHORS file
pkgname=callirhoe
pkgver=195
pkgrel=1
pkgdesc="PDF Calendar creator with high quality vector graphics"
url="https://code.google.com/p/callirhoe/"
arch=('any')
license=('GPLv3')
depends=('python2' 'imagemagick' 'python2-cairo' 'subversion')
source=("$pkgname::svn+https://callirhoe.googlecode.com/svn/branches/phantome")
md5sums=('SKIP')


pkgver() {
    cd "$pkgname"
    svnversion | tr -d [A-z] | sed 's/ *//g'
}

build() {
    cd "${srcdir}/${pkgname}"
    ./make_pkg
}

package() {
    cd "${srcdir}/${pkgname}"
    install -Dm644 COPYING "$pkgdir/usr/share/licenses/$pkgname/COPYING"
    make DESTDIR="$pkgdir/usr" install
}