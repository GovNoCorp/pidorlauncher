from setuptools import setup, find_packages

# Прочитайте зависимости из requirements.txt, если они есть.
# Если нет, просто перечислите их в install_requires.
install_deps = [
  'PyQt5',
  'requests',
]

setup(
  name='pidorlauncher',
  version='1.0.0',
  description='Скачивай крутой софт от GovNo и других разрабов!!',
  author='govnocorp',
  author_email='realriba@atomicmail.io',
  url='https://govnocorp.github.io/pidorlauncher',

  # Автоматически находит все пакеты в директории
  packages=find_packages(exclude=['tests', 'docs']),

  # Указываем зависимости
  install_requires=install_deps,

  # Точка входа: создает исполняемый файл в PATH.
  # Синтаксис: 'имя_команды = package_name.module_name:function_name'
  entry_points={
    'console_scripts': [
      'pidorlauncher = pidorlauncher.main:main', 
    ],
  },

  # Дополнительные метаданные
  license='BSD-3-Clause',
  classifiers=[
    'Programming Language :: Python :: 3',
    'License :: OSI Approved :: MIT License',
    'Operating System :: POSIX :: Linux',
    'Topic :: Desktop Environment',
  ],
)

