# main.py
from executor_limit import execute_strategy_limit
import time

print("Starting Channel Breakout Bot...")
while True:
    execute_strategy_limit()
    time.sleep(20)  #Check every 30 seconds
    
# -21660.04
