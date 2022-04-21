from threading import Lock


class ThreadSafeVariable:
    def __init__(self, value):
        self.__value = value
        self.__lock = Lock()  # Thread safety

    def get(self):
        self.__lock.acquire()
        val = self.__value
        self.__lock.release()

        return val

    def set(self, value):
        self.__lock.acquire()
        self.__value = value
        self.__lock.release()
