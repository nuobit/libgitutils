from distutils.core import setup

setup(name='libgitutils',
      version='0.0.1',
      author="NuoBiT Solutions, S.L., Eric Antones",
      author_email='eantones@nuobit.com',
      package_dir={'libgitutils': 'src'},
      packages=['libgitutils'],
      entry_points={
        'console_scripts': [
            'gitpull=libgitutils.libgitutils:gitpull',
        ],
      },
      install_requires=[
      ],
      url='https://github.com/nuobit/libgitutils',
      keywords=['git', 'lib', 'vcs'],
      license='AGPLv3+',
      platform='Linux',
      description='GIT utils',
      long_description='Wrapper to call GIT command from python',
      classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Operating System :: POSIX :: Linux',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Version Control',
        'Topic :: Software Development :: Version Control :: CVS',
      ]
)
