from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))

try:
  with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()
except FileNotFoundError:
  long_description = 'Скачивай крутой софт от GovNo и других разрабов!!'

setup(
  # --- Основная информация ---
  name='pidorlauncher',
  version='1.0.0',
  author='Ваше Имя',
  author_email='realriba@atomicmail.io',
  description='Скачивай крутой софт от GovNo и других разрабов!!',
  long_description=long_description,
  long_description_content_type='text/markdown',
  url='https://govnocorp.github.io/pidorlauncher',
  license='BSD-3-Clause',

  classifiers=[
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Development Status :: 5 - Production', 
  ],
  
  
  py_modules=['main'], 
  
  install_requires=[
    'requests',
    'pyqt5', 
  ],
  
  entry_points={
    'console_scripts': [
      'pidorlauncher = pidorlauncher.main:main'
    ],
  },

  # Требования к версии Python
  python_requires='>=3.11',
)


