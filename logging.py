class Log:
    enabled = False

    @classmethod
    def log(cls, msg):
        if not cls.enabled:
            return

        print(msg)
