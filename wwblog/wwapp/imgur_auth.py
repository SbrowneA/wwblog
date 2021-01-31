from imgurpython import ImgurClient
import configparser


def authenticate():
    client_id = "621e3052ce5e787"
    client_secret = "c3a358bb2ec093e586aaffe63503e6473c2263eb"
    imgur_username = "wwblog"
    imgur_password = "saychee5e!"
    refresh_token = None
    client = ImgurClient(client_id=client_id, client_secret=client_secret)
    auth_url = client.get_auth_url('pin')
    print(f"AUTH URL{auth_url}")


