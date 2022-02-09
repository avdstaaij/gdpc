"""The repository setup file."""

import pathlib

from setuptools import setup

here = pathlib.Path(__file__).parent.resolve()

setup(name='gdpc',
      version='4.2_dev',
      description='The Generative Design Python Client is a Python-based '
      + 'interface for the Minecraft HTTP Interface mod.\n'
      + 'It was created for use in the '
      + 'Generative Design in Minecraft Competition.',
      long_description=(here / 'README.md').read_text(encoding='utf-8'),
      long_description_content_type='text/markdown',
      url='http://github.com/nilsgawlik/gdmc_http_client_python',
      author='Blinkenlights',
      author_email='blinkenlights@pm.me',
      license='MIT',
      packages=['gdpc'],
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Topic :: Games/Entertainment :: Simulation',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Version Control :: Git'
      ],
      keywords='GDMC, generative design, Minecraft, HTTP, development',
      python_requires='>=3.6, <4',
      project_urls={  # Optional
          'Bug Reports': 'https://github.com/nilsgawlik/gdmc_http_client_python/issues',
          'Official Competition': 'https://gendesignmc.engineering.nyu.edu/',
          'Chat about it on Discord': 'https://discord.gg/V9MW65bD',
          'Source': 'https://github.com/nilsgawlik/gdmc_http_client_python/',
      },
      zip_safe=False)
