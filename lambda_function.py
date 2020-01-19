# -*- coding: utf-8 -*-
from __future__ import print_function
from os import environ
from random import randrange
from fuzzywuzzy import fuzz
from gmusicapi import Mobileclient

class GMusic(Mobileclient):
    def login(self, authtoken=None):
        username  = environ['EMAIL']
        password  = environ['PASSWORD']
        device_id = environ['DEVICE_ID']
        locale    = environ['LOCALE']
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
        if super(GMusic, self).login(username, password, device_id, locale=locale):
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


def build_cardless_audio_speechlet_response(output, should_end_session, url, token, offsetInMilliseconds=0):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
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
    print(event)
    if event['request']['type'] == 'LaunchRequest':
        return get_welcome_response()
    elif event['request']['type'] == 'IntentRequest':
        return on_intent(event)
    elif event['request']['type'] == 'SessionEndedRequest':
        print('on_session_ended')
    elif event['request']['type'].startswith('AudioPlayer'):
        return handle_playback(event)


def get_welcome_response():
    speech_output = 'Welcome to Google Music.'
    reprompt_text = 'Ask for a playlist from your Google Music account.'
    return build_response(build_cardless_speechlet_response(speech_output, reprompt_text, False))


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
    print('started')


def finished(event):
    print('finished')


def stopped(event):
    print("stopped")


def failed(event):
    print('failed')
    if 'error' in event['request']:
        print(event['request']['error'])


def get_help():
    speech_output = 'This skill can play playlists from your Google Music account.'
    card_title = 'Google Music Help'
    return build_response(build_speechlet_response(card_title, speech_output, None, False))


def illegal_action():
    speech_output = 'You can\'t do that with this skill.'
    return build_response(build_short_speechlet_response(speech_output, True))


def do_nothing():
    return build_response({})


def stop():
    speech_output = 'Okay'
    return build_response(build_stop_speechlet_response(speech_output, True))


def on_intent(event):
    intent_name = event['request']['intent']['name']
    if intent_name == 'PlayPlaylistIntent' or intent_name == 'ShufflePlaylistIntent':
        return play_playlist(event)
    elif intent_name == 'AMAZON.ResumeIntent':
        return resume(event)
    elif intent_name == 'AMAZON.NextIntent':
        return skip(event, 1)
    elif intent_name == 'AMAZON.PreviousIntent':
        return skip(event, -1)
    elif intent_name == 'AMAZON.StartOverIntent':
        return skip(event, 0)
    elif intent_name == 'AMAZON.HelpIntent':
        return get_help()
    elif intent_name == 'AMAZON.CancelIntent':
        return do_nothing()
    elif intent_name == "AMAZON.ShuffleOnIntent":
        return change_mode(event, 's', 1)
    elif intent_name == "AMAZON.ShuffleOffIntent":
        return change_mode(event, 's', 0)
    elif intent_name == "AMAZON.LoopOnIntent":
        return change_mode(event, 'l', 1)
    elif intent_name == "AMAZON.LoopOffIntent":
        return change_mode(event, 'l', 0)
    elif intent_name == 'AMAZON.StopIntent' or intent_name == 'AMAZON.PauseIntent':
        return stop()
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
    playlist_name = event['request']['intent']['slots']['playlist_name']['value']
    shuffle_mode = 0
    loop_mode = 1
    if event['request']['intent']['name'] == 'ShufflePlaylistIntent':
        shuffle_mode = 1
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
    if len(best_playlist['tracks']) == 0:
        speech_output = "I'm sorry, I couldn't find any tracks from that album in your library"
        return build_response(build_short_speechlet_response(speech_output, should_end_session))
    next_playing = 0
    if shuffle_mode:
        next_playing = randrange(len(best_playlist['tracks']))
    track_id = best_playlist['tracks'][next_playing]['trackId']
    _dict = {
        'id': best_playlist['id'],
        'p': next_playing,
        's': shuffle_mode,
        'l': loop_mode,
        't': track_id,
        'auth': authtoken,
        }
    next_token = convert_dict_to_token(_dict)
    next_url = api.get_stream_url(trackId)
    card_title = "Google Music"
    speech_output = "Playing " + best_playlist['name']
    speechlet_response = build_audio_speechlet_response(card_title, speech_output, True, next_url, next_token)
    return build_response(speechlet_response)


def nearly_finished(event):
    print('nearly_finished')
    current_token = event['request']['token']
    next_url, next_token, error = get_next_url_and_token(current_token, 1)
    if error is not None:
        return do_nothing()
    audio_response = build_audio_enqueue_response(True, next_url, current_token, next_token)
    return build_response(audio_response)


def get_playlist_from_id(playlists, id):
    best_playlist = None
    for playlist in playlists:
        if playlist['id'] == id:
            best_playlist = playlist
            break
    return best_playlist


def skip(event, skip_by):
    current_token = event['context']['AudioPlayer']['token']
    next_url, next_token, error = get_next_url_and_token(current_token, skip_by)
    if error is not None:
        return build_response(build_short_speechlet_response(error, True))
    speech_output = 'Okay'
    speechlet_response = build_cardless_audio_speechlet_response(speech_output, True, next_url, next_token)
    return build_response(speechlet_response)


def get_next_url_and_token(current_token, skip_by):
    _dict = convert_token_to_dict(current_token)
    authtoken = _dict['auth']
    api = GMusic()
    authtoken = api.login(authtoken)
    playlists = api.get_all_user_playlist_contents()
    id = _dict['id']
    best_playlist = get_playlist_from_id(playlists, id)
    if best_playlist is None:
        return None, None, 'I cannot find the current playlist.'
    now_playing = int(_dict['p'])
    next_playing = now_playing + skip_by
    shuffle_mode = int(_dict['s'])
    if shuffle_mode and skip_by != 0:
        next_playing = randrange(len(best_playlist['tracks']))
    loop_mode = int(_dict['l'])
    if len(best_playlist['tracks']) <= next_playing:
        if loop_mode:
            next_playing = 0
        else:
            return None, None, 'There are no more songs in the playlist.'
    track_id = best_playlist['tracks'][next_playing]['trackId']
    next_url = api.get_stream_url(trackId)
    _dict['p'] = next_playing
    _dict['t'] = track_id
    next_token = convert_dict_to_token(_dict)
    return next_url, next_token, None


def resume(event, offsetInMilliseconds=None):
    if 'token' not in event['context']['AudioPlayer']:
        return get_welcome_response()
    current_token = event['context']['AudioPlayer']['token']
    next_url, next_token, error = get_next_url_and_token(current_token, 0)
    speech_output = 'Okay'
    if offsetInMilliseconds is None:
        speech_output = 'Resuming'
        offsetInMilliseconds = event['context']['AudioPlayer']['offsetInMilliseconds']
    speechlet_response = build_cardless_audio_speechlet_response(speech_output, True, next_url, next_token, offsetInMilliseconds)
    return build_response(speechlet_response)


def change_mode(event, mode, value):
    if 'token' not in event['context']['AudioPlayer']:
        speech_output = 'Nothing is currently playing.'
        return build_response(build_short_speechlet_response(speech_output, True))
    current_token = event['context']['AudioPlayer']['token']
    _dict = convert_token_to_dict(current_token)
    _dict[mode] = str(value)
    current_token = convert_dict_to_token(_dict)
    speech_output = 'Okay'
    offsetInMilliseconds = event['context']['AudioPlayer']['offsetInMilliseconds']
    next_url, next_token, error = get_next_url_and_token(current_token, 0)
    speechlet_response = build_cardless_audio_speechlet_response(speech_output, True, next_url, current_token, offsetInMilliseconds)
    return build_response(speechlet_response)

