# HablarConSara.activity
# A simple hack to attach a chatterbot to speak activity
# Copyright (C) 2008 Sebastian Silva Fundacion FuenteLibre sebastian@fuentelibre.org
#
# Style and structure taken from Speak.activity Copyright (C) Joshua Minor
#
#     HablarConSara.activity is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     HablarConSara.activity is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with HablarConSara.activity.  If not, see <http://www.gnu.org/licenses/>.

import gtk
import gobject
from gettext import gettext as _

import logging
logger = logging.getLogger('speak')

from toolkit.combobox import ComboBox

import bot.aiml
import voice

BOTS = {
    _('Spanish'): { 'name': 'Sara',
                    'brain': 'bot/sara.brn',
                    'predicates': { 'nombre_bot': 'Sara',
                                    'botmaster': 'la comunidad Azucar' } },
    _('English'): { 'name': 'Alice',
                    'brain': 'bot/alice.brn',
                    'predicates': { 'name': 'Alice',
                                    'master': 'the Sugar Community' } } }

# load Standard AIML set for restricted systems
if int([i for i in file('/proc/meminfo').readlines()
        if i.startswith('MemTotal:')][0].split()[1]) < 524288:
    BOTS[_('English')]['brain'] = 'bot/alisochka.brn'

_kernels = {}


def get_default_voice():
    default_voice = voice.defaultVoice()
    if default_voice.friendlyname not in BOTS:
        return voice.allVoices()[_('English')]
    else:
        return default_voice


def get_voices():
    voices = ComboBox()
    for lang in sorted(BOTS.keys()):
        voices.append_item(voice.allVoices()[lang], lang)
    return voices.get_model()


def respond(voice, text):
    return _kernels[voice].respond(text)


def load(activity, voice, sorry=None):
    if voice in _kernels:
        return False

    old_cursor = activity.get_cursor()
    activity.set_cursor(gtk.gdk.WATCH)

    def load_brain():
        is_first_session = (len(_kernels) == 0)

        try:
            brain = BOTS[voice.friendlyname]
            logger.debug('Load bot: %s' % brain)

            kernel = bot.aiml.Kernel()
            kernel.loadBrain(brain['brain'])
            for name, value in brain['predicates'].items():
                kernel.setBotPredicate(name, value)
            _kernels[voice] = kernel
        finally:
            activity.set_cursor(old_cursor)

        if is_first_session:
            hello = _("Hello, I'am a robot \"%s\". Ask me any question.") \
                    % BOTS[voice.friendlyname]['name']
            if sorry:
                hello += ' ' + sorry
            activity.face.say_notification(hello)
        elif sorry:
            activity.face.say_notification(sorry)

    gobject.idle_add(load_brain)
    return True
