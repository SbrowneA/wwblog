from imgurpython import ImgurClient
import configparser


def start():
    # cfg = configparser.ConfigParser()
    # cfg.read('auth.ini')

    client_id = '621e3052ce5e787'
    client_secret = 'c3a358bb2ec093e586aaffe63503e6473c2263eb'
    # client_id = cfg.get('imgur_credentials', 'client_id')
    # client_secret = cfg.get('imgur_credentials', 'client_secret')
    # imgur_username = cfg.get('imgur_credentials', 'imgur_username')
    # imgur_password = cfg.get('imgur_credentials', 'imgur_password')

    client = ImgurClient(client_id=client_id, client_secret=client_secret)
    return client.gallery()
    # return []
    # print(f"{len(items)} items")
    # for i in items:
