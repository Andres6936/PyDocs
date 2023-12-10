from Pydoc.logger.consolelogger import ConsoleLogger


def test():
    console_logger = ConsoleLogger()
    console_logger.informational('Informational Message')


if __name__ == '__main__':
    test()
