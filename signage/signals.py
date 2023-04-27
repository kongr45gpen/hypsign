# signals.py
from django.dispatch.dispatcher import Signal

import logging

# Signal sent whenever the content of a display is updated
display_update_signal = Signal()

# Signal sent whenever a display is connected or disconnected
display_diagnosis = Signal()

# Signal sent to take a screenshot of a screen
take_screenshot_signal = Signal()