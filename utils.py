# utils.py
# Contains re-usable supporting functions & decorators

# ----- Decorators -----

import time

def retry(fcn):
    # Decorator for repeated attempts for function that can randomly fail
    def wrapper(*args, **kwargs):
        nattempts = 30
        delay = 1
        for attempt in range(nattempts):
            try:
                return fcn(*args, **kwargs)
            except:
                print(f"Repeated attempt {fcn.__name__} # {attempt+1} ")
                time.sleep(delay*attempt)
                continue
        else:
            raise Exception(f"Retry failed for {fcn.__name__}")
    return wrapper