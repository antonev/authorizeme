try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name='authorizeme',
    version=__import__('authorizeme').__version__,
    url='https://github.com/antonev/authorizeme',
    license='MIT',
    description='Authorization library for Python',
    author='Anton Evdokimov',
    author_email='antonevv@gmail.co,',
    long_description='Authorization library for Python that can be used '
                     'with or without any Python web framework',
    py_modules=['authorizeme'],
    install_requires=[],
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
    ],
)
