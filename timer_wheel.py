#!/usr/bin/env python3
"""Timer wheel for efficient timeout scheduling."""

class TimerWheel:
    def __init__(self, slots=60, tick_ms=1000):
        self.slots = slots
        self.tick_ms = tick_ms
        self.wheel = [[] for _ in range(slots)]
        self.current = 0
        self.elapsed = 0

    def schedule(self, delay_ms, callback, data=None):
        ticks = max(1, delay_ms // self.tick_ms)
        slot = (self.current + ticks) % self.slots
        rounds = ticks // self.slots
        entry = {"callback": callback, "data": data, "rounds": rounds, "id": id(callback)}
        self.wheel[slot].append(entry)
        return entry

    def cancel(self, entry):
        for slot in self.wheel:
            if entry in slot:
                slot.remove(entry)
                return True
        return False

    def tick(self):
        self.current = (self.current + 1) % self.slots
        self.elapsed += self.tick_ms
        fired = []
        remaining = []
        for entry in self.wheel[self.current]:
            if entry["rounds"] <= 0:
                entry["callback"](entry["data"])
                fired.append(entry)
            else:
                entry["rounds"] -= 1
                remaining.append(entry)
        self.wheel[self.current] = remaining
        return fired

    def advance(self, ms):
        ticks = ms // self.tick_ms
        all_fired = []
        for _ in range(ticks):
            all_fired.extend(self.tick())
        return all_fired

    def pending(self):
        return sum(len(slot) for slot in self.wheel)

if __name__ == "__main__":
    tw = TimerWheel(slots=10, tick_ms=100)
    results = []
    tw.schedule(500, lambda d: results.append(d), "timer1")
    tw.schedule(1000, lambda d: results.append(d), "timer2")
    tw.advance(1500)
    print(f"Fired: {results}")

def test():
    tw = TimerWheel(slots=10, tick_ms=100)
    results = []
    tw.schedule(300, lambda d: results.append(d), "a")
    tw.schedule(500, lambda d: results.append(d), "b")
    tw.schedule(800, lambda d: results.append(d), "c")
    assert tw.pending() == 3
    tw.advance(400)
    assert results == ["a"]
    tw.advance(200)
    assert results == ["a", "b"]
    tw.advance(300)
    assert results == ["a", "b", "c"]
    assert tw.pending() == 0
    # Cancel
    tw2 = TimerWheel(slots=10, tick_ms=100)
    entry = tw2.schedule(500, lambda d: None, "x")
    assert tw2.pending() == 1
    tw2.cancel(entry)
    assert tw2.pending() == 0
    print("  timer_wheel: ALL TESTS PASSED")
