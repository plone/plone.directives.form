from setuptools import setup, find_packages
import os

version = '1.1dev'

setup(name='plone.directives.form',
      version=version,
      description="Grok-like directives configuring forms",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='grok plone dexterity form content',
      author='Martin Aspeli',
      author_email='optilude@gmail.com',
      url='http://code.google.com/p/dexterity',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone', 'plone.directives'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'zope.deferredimport',
          'five.grok>=1.0b2',
          'plone.autoform>=1.1dev',
          'plone.z3cform>=0.6.0',
          'Products.statusmessages',
          'plone.supermodel>=1.1dev',
          'zope.i18nmessageid',
          'zope.publisher',
          'plone.rfc822',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
