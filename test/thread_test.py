import threading
import time

class Example:
    def __init__(self):
        pass

    def task1(self):
        print("Sleeping for 1 second for task1")
        time.sleep(1)
        print("Executing task1")

    def task2(self):
        print("Sleeping for 1 second for task2")
        time.sleep(1)
        print("Executing task2")


    def initThread(self):
        thread1 = threading.Thread(target=self.task1)
        thread2 = threading.Thread(target = self.task2)
        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()
        ##
        

ex = Example()
ex.initThread()
