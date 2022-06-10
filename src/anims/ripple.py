from math import pi, sin
from anims.tween import TweenAnim
from lib.filters import ripple as _ripple


class RippleAnim(TweenAnim):

    def ripple(anim, *args, amplitude=0, **kwargs):
        amplitude = amplitude or max(1, sin(anim.pos * pi) * 2) * 2
        return _ripple(amplitude=amplitude, *args, **kwargs)
