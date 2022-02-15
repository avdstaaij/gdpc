"""The repository setup file."""

from setuptools import find_packages, setup

__author__ = "Blinkenlights"
__version__ = "v4.3_dev"

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fh:
    requirements = fh.readlines()

setup(name='gdpc',
      version='4.3_dev',
      description='The Generative Design Python Client is a Python-based '
      + 'interface for the Minecraft HTTP Interface mod.\n'
      + 'It was created for use in the '
      + 'Generative Design in Minecraft Competition.',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='http://github.com/nilsgawlik/gdmc_http_client_python',
      author='Blinkenlights',
      author_email='blinkenlights@pm.me',
      license='MIT',
      packages=find_packages(),
      install_requires=[req for req in requirements if req[:2] != "# "],
      python_requires='>=3.6, <4',
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
      project_urls={  # Optional
          'Bug Reports': 'https://github.com/nilsgawlik/gdmc_http_client_python/issues',
          'Official Competition': 'https://gendesignmc.engineering.nyu.edu/',
          'Chat about it on Discord': 'https://discord.gg/V9MW65bD',
          'Source': 'https://github.com/nilsgawlik/gdmc_http_client_python/',
      },
      zip_safe=False)
