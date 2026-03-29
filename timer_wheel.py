#!/usr/bin/env python3
"""timer_wheel - Hierarchical timer wheel for efficient timeout management."""
import sys

class TimerWheel:
    def __init__(self, slots=60, tick_ms=1000):
        self.slots = slots
        self.tick_ms = tick_ms
        self.wheel = [[] for _ in range(slots)]
        self.current = 0
        self.elapsed = 0
        self.timer_id = 0

    def add(self, delay_ms, callback, data=None):
        ticks = max(1, delay_ms // self.tick_ms)
        slot = (self.current + ticks) % self.slots
        tid = self.timer_id
        self.timer_id += 1
        self.wheel[slot].append({"id": tid, "callback": callback, "data": data, "remaining_rounds": ticks // self.slots})
        return tid

    def cancel(self, timer_id):
        for slot in self.wheel:
            slot[:] = [t for t in slot if t["id"] != timer_id]

    def tick(self):
        self.current = (self.current + 1) % self.slots
        self.elapsed += self.tick_ms
        fired = []
        remaining = []
        for timer in self.wheel[self.current]:
            if timer["remaining_rounds"] <= 0:
                timer["callback"](timer["data"])
                fired.append(timer["id"])
            else:
                timer["remaining_rounds"] -= 1
                remaining.append(timer)
        self.wheel[self.current] = remaining
        return fired

    def advance(self, ticks):
        all_fired = []
        for _ in range(ticks):
            all_fired.extend(self.tick())
        return all_fired

    def pending(self):
        return sum(len(slot) for slot in self.wheel)

def test():
    tw = TimerWheel(slots=10, tick_ms=100)
    results = []
    tw.add(300, lambda d: results.append(d), "timer1")
    tw.add(500, lambda d: results.append(d), "timer2")
    tw.add(300, lambda d: results.append(d), "timer3")
    assert tw.pending() == 3
    fired = tw.advance(3)
    assert "timer1" in results
    assert "timer3" in results
    assert "timer2" not in results
    tw.advance(2)
    assert "timer2" in results
    assert tw.pending() == 0
    tid = tw.add(200, lambda d: results.append("cancelled"), "x")
    tw.cancel(tid)
    tw.advance(5)
    assert "cancelled" not in results
    print("All tests passed!")

if __name__ == "__main__":
    test() if "--test" in sys.argv else print("timer_wheel: Timer wheel. Use --test")
