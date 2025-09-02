# main.py
from executor_limit import execute_strategy_limit
import time

print("Starting Channel Breakout Bot...")
# while True:
#     execute_strategy_limit()
#     time.sleep(10)  #Check every 30 seconds
    
# import time
from datetime import datetime

while True:
    now = datetime.now()
    current_second = now.second

    # Run strategy only if second is between 1 and 5
    if (0 <= current_second <= 2 or 6 <= current_second <= 9 or 13 <= current_second <= 15 or 18 <= current_second <= 20 
        or 24 <= current_second <= 26 or 30 <= current_second <= 32 or 36 <= current_second <= 38 or 42 <= current_second <= 44
        or 48 <= current_second <= 50 or 55 <= current_second <= 57):
        execute_strategy_limit()  # your function
        # print("HUhuhuhuu : ", current_second)
        time.sleep(4)
    else:
        # Sleep a small amount to reduce CPU usage
        # print(current_second)
        time.sleep(1)
