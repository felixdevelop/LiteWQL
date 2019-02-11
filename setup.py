import os
from setuptools import setup, find_packages


def read(fn):
    path = os.path.join(os.path.dirname(__file__), fn)
    try:
        file = open(path, encoding='utf-8')
    except TypeError:
        file = open(path)
    return file.read()


setup(
    name='litewql',
    version=__import__('litewql').VERSION,
    description='Lite web queries language',
    long_description=read('README.md'),
    long_description_content_type="text/markdown",
    author='Vadim Sharay',
    author_email='vadimsharay@gmail.com',
    packages=find_packages(exclude=['tests']),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        "regex"
    ],
    classifiers=[
            'Development Status :: 2 - Pre-Alpha',
            # 'Development Status :: 3 - Alpha',
            # 'Development Status :: 4 - Beta',
            # 'Development Status :: 5 - Production/Stable',
            # 'Development Status :: 6 - Mature',
            # 'Development Status :: 7 - Inactive',
            'Intended Audience :: Developers',
            'Intended Audience :: End Users/Desktop',
            'Intended Audience :: Information Technology',
            'Intended Audience :: Science/Research',
            'Intended Audience :: System Administrators',
            'License :: OSI Approved :: BSD License',
            'Operating System :: POSIX',
            'Operating System :: MacOS',
            'Operating System :: Unix',
            'Programming Language :: Python',
            # 'Programming Language :: Python :: 2',
            # 'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            "Programming Language :: Python :: Implementation :: PyPy3",
            'Topic :: Software Development :: Libraries'
    ]
)
