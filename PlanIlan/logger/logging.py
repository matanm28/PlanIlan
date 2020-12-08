import logging
import sys


def configure_logging():
    file_handler = logging.FileHandler(filename='{0}/{1}.log'.format('logging', 'database_builder'),
                                       mode='w', encoding='utf-8')
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)-4s - %(message)s',
                        datefmt='%d.%m.%y-%H-%M-%S',
                        handlers=[file_handler])

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('[%(levelname)s] - %(message)s')
    console_handler.setFormatter(console_formatter)
    logging.getLogger().addHandler(console_handler)


if __name__ == '__main__':
    configure_logging()
