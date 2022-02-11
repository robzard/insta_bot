import docker
import os

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
if __name__ == '__main__':
    images = ''
    client = docker.from_env()
    images_list = [images + str(el) for el in client.images.list()]
    if 'bot_worker' not in str(images_list):
        client.images.build(path=ROOT_DIR,
                            tag='bot_worker')
    client.containers.run('bot_worker', detach=True)