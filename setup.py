from distutils.core import setup

setup(
    name='Slack_Reporter',
    version='0.0.1',
    author=['Michal Wozniak'],
    packages=["Slack_Reporter"],
    scripts=[],
    url='https://github.com/mv740/BuildBot-Slack-Reporter',
    license='LICENSE.txt',
    description='slack reporter plugin for buildbot',
    long_description=open('README.md').read(),
    install_requires=[
        "buildbot >= 1.4.0",
    ],
    keywords=["buildbot", "slack", "monitoring"],
    entry_points = {
            'buildbot.reporters': 'slack = Slack_Reporter:SlackStatusPush'}
)
