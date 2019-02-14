from distutils.core import setup

setup(
    name='Slack-Reporter',
    version='0.0.1',
    author=['Michal Wozniak'],
    packages=[],
    scripts=[],
    url='https://github.com/mv740/BuildBot-Slack-Reporter',
    license='LICENSE.txt',
    description='slack reporter plugin for buildbot',
    long_description=open('README.md').read(),
    install_requires=[
        "buildbot >= 1.4.0",
    ],
)