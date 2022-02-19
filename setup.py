"""The repository setup file."""

from setuptools import find_packages, setup

__author__ = "Blinkenlights"
__version__ = "v5.0.2"

with open("README.md", "r") as readme:
    long_description = readme.read()

setup(name='gdpc',
      version=__version__,
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
      install_requires=['matplotlib',
                        'NBT',
                        'numpy',
                        'opencv_python',
                        'requests'],
      python_requires='>=3.6, <4',
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Topic :: Games/Entertainment :: Simulation',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Version Control :: Git'
      ],
      keywords='GDMC, generative design, Minecraft, HTTP, development',
      project_urls={
          'Bug Reports': 'https://github.com/nilsgawlik/gdmc_http_client_python/issues',
          'Official Competition': 'https://gendesignmc.engineering.nyu.edu/',
          'Chat about it on Discord': 'https://discord.gg/V9MW65bD',
          'Source': 'https://github.com/nilsgawlik/gdmc_http_client_python/',
      },
      zip_safe=False)
