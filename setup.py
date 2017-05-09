from setuptools import setup, find_packages

version = '2.0.3'

tests_require = []


setup(name='plone.directives.form',
      version=version,
      description="Grok-like directives configuring forms",
      long_description=(open("README.rst").read() + "\n" +
                        open("CHANGES.rst").read()),
      # Get more strings from
      # https://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Framework :: Plone",
          "Framework :: Plone :: 4.3",
          "Framework :: Plone :: 5.0",
          "Framework :: Plone :: 5.1",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Topic :: Software Development :: Libraries :: Python Modules",
          ],
      keywords='grok plone dexterity form content',
      author='Martin Aspeli',
      author_email='optilude@gmail.com',
      url='https://github.com/plone/plone.directives.form',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone', 'plone.directives'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'zope.deferredimport',
          'five.grok>=1.0b2',
          'grokcore.view>=2.2',
          'plone.autoform>=1.2dev',
          'plone.z3cform>=0.6.0',
          'Products.statusmessages',
          'plone.supermodel>=1.1dev',
          'zope.i18nmessageid',
          'zope.publisher',
          'plone.rfc822',
          # -*- Extra requirements: -*-
      ],
      tests_require=tests_require,
      extras_require={'test': tests_require},
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
