import select
from typing import Any, Literal, Sequence, TypedDict

from .const import Axis, Button, Configuration


class EnvelopeEffect(TypedDict):
    type: Literal["constant", "ramp"]
    attack_length: int
    attack_level: int
    fade_length: int
    fade_level: int


class ConditionSide(TypedDict):
    # TODO: replace with enums
    right_saturation: int
    left_saturation: int
    right_coeff: int
    left_coeff: int
    deadband: int
    center: int


class RumbleEffect(TypedDict):
    type: Literal["rumble"]
    strong_magnitude: float
    weak_magnitude: float


class ConditionEffect(TypedDict):
    type: Literal["condition"]
    left: ConditionSide
    right: ConditionSide


class PeriodicEffect(TypedDict):
    type: Literal["periodic"]
    # Todo: replace with enums
    waveform: int
    period: int
    magnitude: int
    offset: int
    phase: int

    attack_length: int
    attack_level: int
    fade_length: int
    fade_level: int

    custom: bytes


class EffectEvent(TypedDict):
    # Always effect, better for filterring
    type: Literal["effect"]
    # Event target. Not part of the standard but required for e.g., DS5.
    code: Literal["main", "left", "right"]

    id: int
    # TODO: Upgrade to literal
    direction: int

    trigger_button: str
    trigger_interval: int

    replay_length: int
    replay_delay: int

    effect: EnvelopeEffect | ConditionEffect | PeriodicEffect | RumbleEffect


class RgbLedEvent(TypedDict):
    """Inspired by new controllers with RGB leds, especially below the buttons.

    Instead of code, this event type exposes multiple properties, including mode."""

    type: Literal["led"]

    # The led
    code: Literal["main", "left", "right"]

    # Various lighting modes supported by the led.
    mode: Literal["disable", "solid", "blinking", "rainbow", "spiral"]

    # Brightness range is from 0 to 1
    # If the response device does not support brightness control, it shall
    # convert the rgb color to hue, assume saturation is 1, and derive a new
    # RGB value from the brightness below
    brightness: float

    # The speed the led should blink if supported by the led
    speed: float

    # Color values for the led, may be ommited depending on the mode, by being
    # set to 0
    red: int
    green: int
    blue: int


class ButtonEvent(TypedDict):
    type: Literal["button"]
    code: Button
    value: bool


class AxisEvent(TypedDict):
    type: Literal["axis"]
    code: Axis
    value: float


class ConfigurationEvent(TypedDict):
    type: Literal["configuration"]
    code: Configuration
    value: Any


Event = EffectEvent | ButtonEvent | AxisEvent | ConfigurationEvent


class Producer:
    def open(self) -> Sequence[int]:
        """Opens and returns a list of file descriptors that should be listened to."""
        raise NotImplementedError()

    def close(self, exit: bool) -> bool:
        """Called to close the device.

        If `exit` is true, the program is about to
        close. If it is false, the controller is entering power save mode because
        it is unused. In this case, if this service is required, you may forgo
        closing and return false. If true, it is assumed this producer is closed.

        `open()` will be called again once the consumers are ready."""
        return False

    def produce(self, fds: Sequence[int]) -> Sequence[Event]:
        """Called with the file descriptors that are ready to read."""
        raise NotImplementedError()


class Consumer:
    available: bool
    """Hint that states if the consumer can receive events. If it is false,
    consumer will not be called. If all consumers are false, producers will
    be closed to save CPU utilisation."""

    def initialize(self):
        """Optional method for initialization."""
        pass

    def consume(self, events: Sequence[Event]):
        pass


def can_read(fd: int):
    return select.select([fd], [], [], 0)[0]