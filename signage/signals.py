# signals.py
from django.dispatch.dispatcher import Signal

import logging

# Signal sent whenever the content of a display is updated
display_update_signal = Signal()

# Signal sent whenever a display is connected or disconnected
display_connect_signal = Signal()
