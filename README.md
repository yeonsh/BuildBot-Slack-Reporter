# BuildBot-Slack-Reporter


## How to use 


#### In master.cfg
```
SlackChannelMap = {
    "runtests" : "test"
}

custom_message_property = {
    "runtests" : ["TAG"]
}


slackReporter = reporters.SlackStatusPush("slack_bot_token"),
                                                        endpoint='https://slack.com',
                                                        builder_room_map=SlackChannelMap,
                                                        builder_custom_message_property=custom_message_property,
                                                        wantProperties=True
                                                        )

c['services'].append(slackReporter)
```

## Settings 

- slack_bot_token : https://get.slack.help/hc/en-us/articles/215770388-Create-and-regenerate-API-tokens
  - using /api/chat.postMessage  to send messages

- builder_room_map : slack channels mapping
  - whenever builder named runtests is processed, all messages will be send to the "test" channel

- custom_message_property : Add extra properties created during your build in the slack message
  -  dict ( buildername - List of properties ) 
  - eg : TAG will create in one of runtests buildstep and will appear in the message
  

