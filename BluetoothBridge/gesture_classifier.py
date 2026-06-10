import time
from enum import Enum, auto


class Command(Enum):
    NONE = auto()
    LEFT = auto()
    RIGHT = auto()
    FORWARD = auto()
    BACKWARD = auto()
    JUMP = auto()


class GestureClassifier:

    ALPHA = 0.08
    MIN_STD = 300.0
    COOLDOWN = 0.7
    Z_FWD_BWD = 3.0
    Z_LR = 3.0
    Z_JUMP = 3.0

    def __init__(self):
        self._bx = self._by = self._bz = None
        self._jump_locked  = False
        self._last_cmd_time = 0.0

    def classify(self, x: float, y: float, z: float) -> Command:
        if self._bx is None:
            self._bx=x
            self._by=y
            self._bz=z
            print("FIRST PACKET")
            return Command.NONE

        zx = (x-self._bx) / self.MIN_STD
        zy = (y-self._by) / self.MIN_STD
        zz = (z-self._bz) / self.MIN_STD

        if abs(zx)<1.2 and abs(zy)<1.2 and abs(zz)<1.2:
            print(f"zx={zx:.2f} zy={zy:.2f} zz={zz:.2f}")
            rest = True
        else:
            rest = False

        if rest:
            a = self.ALPHA
            self._bx = (1-a)*self._bx + a*x
            self._by = (1-a)*self._by + a*y
            self._bz = (1-a)*self._bz + a*z

        if zz>self.Z_JUMP:
            if not self._jump_locked:
                self._jump_locked = True
                return Command.JUMP
            return Command.NONE
        
        else:
            self._jump_locked = False

        if time.time()-self._last_cmd_time < self.COOLDOWN:
            return Command.NONE
        
        best_score = 0.0
        cmd = Command.NONE

        # Accelorometer y

        if abs(zy)>= self.Z_FWD_BWD and abs(zy)>best_score:
            best_score = abs(zy)
            if zy>0:
                cmd = Command.FORWARD
            else:
                cmd = Command.BACKWARD

        # Accelorometer x

        if abs(zx)>=self.Z_LR and abs(zx)>best_score:
            best_score = abs(zx)
            if zx>0:
                cmd = Command.RIGHT
            else:
                cmd = Command.LEFT
        if cmd != Command.NONE:
            self._last_cmd_time = time.time()

        return cmd
