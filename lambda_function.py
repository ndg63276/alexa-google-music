# -*- coding: utf-8 -*-
from __future__ import print_function
from os import environ
from fuzzywuzzy import fuzz


class GMusic(Mobileclient):
    def login(self, authtoken=None):
        username  = environ['EMAIL']
        password  = environ['PASSWORD']
        device_id = environ['DEVICE_ID']
        if authtoken is not None:
            self.android_id               = device_id
            self.session._authtoken       = authtoken
            self.session.is_authenticated = True
            try:
                # Send a test request to ensure our authtoken is still valid and working
                self.get_registered_devices()
                return authtoken
            except:
                # Failed with the test-request so we set "is_authenticated=False"
                # and go through the login-process again to get a new "authtoken"
                self.session.is_authenticated = False
        if super(GMusic, self).login(username, password, device_id, locale='en_GB'):
            return self.session._authtoken
        # Prevent further execution in case we failed with the login-process
        return False


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_audio_speechlet_response(title, output, should_end_session, url, token, offsetInMilliseconds=0):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': output
        },
        'directives': [{
            'type': 'AudioPlayer.Play',
            'playBehavior': 'REPLACE_ALL',
            'audioItem': {
                'stream': {
                    'token': str(token),
                    'url': url,
                    'offsetInMilliseconds': offsetInMilliseconds
                }
            }
        }],
        'shouldEndSession': should_end_session
    }
    

def build_audio_enqueue_response(should_end_session, url, previous_token, next_token, playBehavior='ENQUEUE'):
    to_return = {
        'directives': [{
            'type': 'AudioPlayer.Play',
            'playBehavior': playBehavior,
            'audioItem': {
                'stream': {
                    'token': str(next_token),
                    'url': url,
                    'offsetInMilliseconds': 0
                }
            }
        }],
        'shouldEndSession': should_end_session
    }
    if playBehavior == 'ENQUEUE':
        to_return['directives'][0]['audioItem']['stream']['expectedPreviousToken'] = str(previous_token)
    return to_return


def build_stop_speechlet_response(output, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'directives': [{
            'type': 'AudioPlayer.Stop'
        }],
        'shouldEndSession': should_end_session
    }


def build_short_speechlet_response(output, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'shouldEndSession': should_end_session
    }


def build_cardless_speechlet_response(output, reprompt_text, should_end_session, speech_type='PlainText'):
    text_or_ssml = 'text'
    if speech_type == 'SSML':
        text_or_ssml = 'ssml'
    return {
        'outputSpeech': {
            'type': speech_type,
            text_or_ssml: output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(speechlet_response, sessionAttributes={}):
    return {
        'version': '1.0',
        'sessionAttributes': sessionAttributes,
        'response': speechlet_response
    }


def lambda_handler(event, context):
    if event['request']['type'] == 'LaunchRequest':
        return get_welcome_response(event)
    elif event['request']['type'] == 'IntentRequest':
        return on_intent(event)
    elif event['request']['type'] == 'SessionEndedRequest':
        logger.info('on_session_ended')
    elif event['request']['type'].startswith('AudioPlayer'):
        return handle_playback(event)


def get_welcome_response():
    speech_output = 'Welcome to Google Music.'
    reprompt_text = 'Ask for a playlist from your Google Music account.'
    should_end_session = False
    return build_response(build_cardless_speechlet_response(speech_output, reprompt_text, should_end_session))


def handle_playback(event):
    request = event['request']
    if request['type'] == 'AudioPlayer.PlaybackStarted':
        return started(event)
    elif request['type'] == 'AudioPlayer.PlaybackFinished':
        return finished(event)
    elif request['type'] == 'AudioPlayer.PlaybackStopped':
        return stopped(event)
    elif request['type'] == 'AudioPlayer.PlaybackNearlyFinished':
        return nearly_finished(event)
    elif request['type'] == 'AudioPlayer.PlaybackFailed':
        return failed(event)


def started(event):
    logger.info('started')


def finished(event):
    logger.info('finished')


def stopped(event):
    logger.info("stopped")


def failed(event):
    logger.info('failed')


def nearly_finished(event):
    logger.info('nearly_finished')


def get_help():
    speech_output = 'This skill can play playlists from your Google Music account. '
    card_title = 'Google Music Help'
    should_end_session = False
    return build_response(build_speechlet_response(card_title, speech_output, None, should_end_session))


def illegal_action():
    speech_output = 'You can\'t do that with this skill.'
    should_end_session = True
    return build_response(build_short_speechlet_response(speech_output, should_end_session))


def do_nothing():
    return build_response({})


def on_intent(event):
    intent_name = event['request']['intent']['name']
    if intent_name == 'PlayPlaylistIntent':
        return play_playlist(event)
    elif intent_name == 'AMAZON.HelpIntent':
        return get_help()
    elif intent_name == 'AMAZON.CancelIntent':
        return do_nothing()
    elif intent_name == 'AMAZON.StopIntent' or intent_name == 'AMAZON.PauseIntent':
        return stop(intent, session)
    else:
        raise ValueError("Invalid intent")


def convert_token_to_dict(token):
    pi = token.split('&')
    _dict = {}
    for i in pi:
        key = i.split('=')[0]
        val = i.split('=')[1]
        _dict[key] = val
    return _dict


def convert_dict_to_token(_dict):
    token = '&'.join(['='.join([key, str(val)]) for key, val in _dict.items()])
    return token


def play_playlist(event):
    song_ids = []
    playlist_name = event['request']['intent']['slots']['playlist_name']['value']
    should_end_session = True
    api = GMusic()
    authtoken = api.login()
    if authtoken is False:
        speech_output = 'Sorry, login failed.'
        return build_response(build_short_speechlet_response(speech_output, should_end_session))
    playlists = api.get_all_user_playlist_contents()
    best_match = 0
    best_playlist = None
    for playlist in playlists:
        match = fuzz.ratio(playlist_name.lower(), playlist['name'].lower())
        if match > 50 and match > best_match:
            best_match = match
            best_playlist = playlist
    if best_playlist is None:
        speech_output = 'Sorry, I couldn\'t find the playlist ' + playlist_name
        return build_response(build_short_speechlet_response(speech_output, should_end_session))
    for track in best_playlist['tracks']:
        song_ids.append(track['trackId'])
    if len(song_ids) == 0:
        speech_output = "I'm sorry, I couldn't find any tracks from that album in your library"
        return build_response(build_short_speechlet_response(speech_output, should_end_session))
    next_token = 0
    next_url = get_url(song_ids[next_token], api)
    card_title = "Google Music"
    speech_output = "Playing " + best_playlist['name']
    return build_response(build_audio_speechlet_response(card_title, speech_output, should_end_session, next_url, next_token))

