import random
import time

def random_delay(min_s: float, max_s: float):
    d = random.uniform(min_s, max_s)
    print(f"[i] Delay {d:.1f}s to be polite...")
    time.sleep(d)