pkgname=pidorlauncher
pkgver=1.0.0
pkgrel=1
pkgdesc='Скачивай крутой софт от GovNo и других разрабов!!'
arch=('any') 
url='https://govnocorp.github.io/pidorlauncher'
license=('BSD-3-Clause')
depends=(python python-requests python-pyqt5)
makedepends=(python-setuptools)
source=("https://github.com/GovNoCorp/pidorlauncher/archive/refs/tags/v${pkgver}.tar.gz")
sha256sums=('SKIP')

package() {
  cd "${srcdir}/pidorlauncher-${pkgver}" 
  python -m pip install --root="$pkgdir"
  install -Dm644 "pidorlauncher.desktop" "$pkgdir/usr/share/applications/pidorlauncher.desktop"
  install -Dm644 "pidorlauncher.png" "$pkgdir/usr/share/icons/hicolor/256x256/apps/pidorlauncher.png"
}



