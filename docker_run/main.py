import docker
import os

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
if __name__ == '__main__':
    for i in range(0,2):
        print(i)
    images = ''
    client = docker.from_env()
    containers_list = len(client.containers.list(filters={'status': 'exited'}))
    images_list = [images + str(el) for el in client.images.list()]
    if 'bot_worker' not in str(images_list):
        client.images.build(path=ROOT_DIR,
                            tag='bot_worker')
    client.containers.run('bot_worker', detach=True)
