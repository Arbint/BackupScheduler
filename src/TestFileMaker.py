import os
import time

count = 0
while True:
    count+=1
    fileName = f"/opt/perforce/perforce_pool/newFile_{count}.txt"
    with open(fileName, "w") as file:
        print(f"saving file: {fileName}")
        
    time.sleep(2)


