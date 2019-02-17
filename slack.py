from future.utils import string_types

from twisted.internet import defer

from buildbot import config
from buildbot.process.results import statusToString
from buildbot.reporters import utils
from buildbot.reporters.http import HttpStatusPushBase
from buildbot.util import httpclientservice
from buildbot.util.logger import Logger

import utility as util

log = Logger()

HOSTED_BASE_URL = "https://slack.com"


class SlackStatusPush(HttpStatusPushBase):
    name = "SlackStatusPush",
    namespace = 'buildbot'


    #map buildbot to slack color 
    BUILD_RESULT = {
        'success': '#8d4',
        'warnings': 'warning',
        'failure': '#ff0000', #red
        'skipped': '#AADDEE',
        'exception': '#c6c',
        'retry': '#ecc',
        'cancelled': '#ecc',
        'not finished' : 'warning',
        'Invalid status': 'warning'
    }



    def checkConfig(self, auth_token, endpoint=HOSTED_BASE_URL,
                    builder_room_map=None, builder_user_map=None,
                    event_messages=None, builder_custom_message_property=None, **kwargs):
        if not isinstance(auth_token, string_types):
            config.error('auth_token must be a string')
        if not isinstance(endpoint, string_types):
            config.error('endpoint must be a string')
        if builder_room_map and not isinstance(builder_room_map, dict):
            config.error('builder_room_map must be a dict')
        if builder_user_map and not isinstance(builder_user_map, dict):
            config.error('builder_user_map must be a dict')
        if builder_custom_message_property and not isinstance(builder_custom_message_property, dict):
            config.error('builder_custom_message_property must be a dict')
            

    @defer.inlineCallbacks
    def reconfigService(self, auth_token, endpoint="https://slack.com",
                        builder_room_map=None, builder_user_map=None,
                        event_messages=None,builder_custom_message_property=None, **kwargs):
        auth_token = yield self.renderSecrets(auth_token)
        yield HttpStatusPushBase.reconfigService(self, **kwargs)
        self._http = yield httpclientservice.HTTPClientService.getService(
            self.master, endpoint,
            debug=self.debug, verify=self.verify)

        token_format = 'Bearer %s' % (auth_token)
        self.auth_token = token_format
        self.builder_room_map = builder_room_map
        self.builder_user_map = builder_user_map
        self.builder_custom_message_property = builder_custom_message_property

    # returns a Deferred that returns None
    def buildStarted(self, key, build):
        return self.send(build, key[2])

    # returns a Deferred that returns None
    def buildFinished(self, key, build):
        return self.send(build, key[2])

    @defer.inlineCallbacks
    def getBuildDetailsAndSendMessage(self, build, key):
        yield utils.getDetailsForBuild(self.master, build, **self.neededDetails)
        postData = yield self.getRecipientList(build, key)
        postData['message'] = yield self.getMessage(build, key)
        extra_params = yield self.getExtraParams(build, key)
        postData.update(extra_params)
        defer.returnValue(postData)

    def getRecipientList(self, build, event_name):
        result = {}
        builder_name = build['builder']['name']
        if self.builder_user_map and builder_name in self.builder_user_map:
            result['id_or_email'] = self.builder_user_map[builder_name]
        if self.builder_room_map and builder_name in self.builder_room_map:
            result['room_id_or_name'] = self.builder_room_map[builder_name]
        return result

    def getCustomMessageProperties(self, build, event_name):
        builder_name = build['builder']['name']
        if self.builder_custom_message_property and builder_name in self.builder_custom_message_property:
            return self.builder_custom_message_property[builder_name]
        return None

    def getMessage(self, build, event_name):
        event_messages = {
            'new': 'Buildbot started build %s here: %s' % (build['builder']['name'], build['url']),
            'finished': 'Buildbot finished build %s with result %s here: %s'
                        % (build['builder']['name'], statusToString(build['results']), build['url'])
        }
        return event_messages.get(event_name, '')

    # use this as an extension point to inject extra parameters into your
    # postData
    @defer.inlineCallbacks
    def getExtraParams(self, build, event_name):
        result = {}

        state_message = build['state_string']  # // build text
        build_url = build['url']
        builder_name = build['builder']['name']
        build_number = build['number']

        result['slack_message'] = {
                "channel" : "",
                "attachments": [
                    {
                        "fallback": "%s - %s" % (state_message,build_url),
                        "text": "<%s|%s # %s> - %s" %(build_url, builder_name, build_number,state_message),
                        "color": self.BUILD_RESULT[statusToString(build['results'])]
                    }
                ]
            }

	
        # basic message for new event 
        if event_name == 'new':
            defer.returnValue(result)

        
        
        # build finished message
        build_properties = build.get('properties')
        if build_properties is not None:
            #warning please use util.GetBuildPropertyValue(build_property, property_name)

            build_commit_description = util.GetBuildPropertyValue(build_properties, 'commit-description')
    
            build_worker_name = util.GetBuildPropertyValue(build_properties,'workername') # for environment

            #https://api.slack.com/docs/messages#how_to_send_messages
            result['slack_message']['attachments'][0]['fields'] = []

            message_fields =  result['slack_message']['attachments'][0]['fields']
            if build_commit_description is not None:
                commit_field = {
                                    "title": "Tag",
                                    "value": build_commit_description,
                                    "short": "true"
                                }
                message_fields.append(commit_field)

            if build_worker_name is not None:
                worker_name_field = {
                                    "title": "Worker",
                                    "value": build_worker_name,
                                    "short": "true"
                                }
                message_fields.append(worker_name_field)

            #add custom property
            custom_message_properties = yield self.getCustomMessageProperties(build, event_name)
            if custom_message_properties is not None:
                for custom_property in custom_message_properties:
                    custom_property_value = util.GetBuildPropertyValue(build_properties,custom_property) # for environment
                    custom_property_field = {
                                    "title": custom_property,
                                    "value": custom_property_value,
                                    "short": "true"
                                }
                    message_fields.append(custom_property_field)

            # Add Reponsable Users Field 
            blamelist = yield utils.getResponsibleUsersForBuild(self.master, build['buildid'])
            if len(blamelist) > 0:
                blamelist_str = ''.join(blamelist)

                blameField =  {
                                    "title": "Responsable Users",
                                    "value": blamelist_str,
                                    "short": "true"
                                }
                message_fields.append(blameField)
        defer.returnValue(result)

    # TODO : send slack message using api
    @defer.inlineCallbacks
    def send(self, build, key):
        postData = yield self.getBuildDetailsAndSendMessage(build, key)
        print("print postData object")
        util.PrintDict(postData)
        if not postData or 'message' not in postData or not postData['message'] :
            return

        if 'slack_message' not in postData or not postData['slack_message'] :
            return

        
        message = postData['slack_message'] 
        postDataSlack = message
        postDataSlack["channel"] = postData["room_id_or_name"]



        urls = []
        urls.append('/api/chat.postMessage')

        # if 'id_or_email' in postData:
        #     urls.append('/v2/user/{}/message'.format(postData.pop('id_or_email')))
        # if 'room_id_or_name' in postData:
        #     urls.append('/v2/room/{}/notification'.format(postData.pop('room_id_or_name')))

        #####
        # https://slack.com/api/chat.postMessage    
            
        for url in urls:
            response = yield self._http.post(url, headers={'Authorization': self.auth_token}, json=postDataSlack)
            if response.code != 200:
                content = yield response.content()
                log.error("Slack Reporter {code}: unable to upload status: {content}",
                    code=response.code, content=content)
