from httpx import Client


def make_register_request(client: Client, username: str, password: str):
    url = "http://127.0.0.1:8000/api/auth/register/"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "username": username,
        "password": password
    }

    r = client.post(url, headers=headers, json=data)

    return r.json()


def make_login_request(client: Client, username: str, password: str):
    url = "http://127.0.0.1:8000/api/auth/login/"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "username": username,
        "password": password
    }

    r = client.post(url, headers=headers, json=data)

    return r.json()


def make_logout_request(client: Client, refresh_token: str):
    url = "http://127.0.0.1:8000/api/auth/logout/"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "refresh": refresh_token
    }

    r = client.post(url, headers=headers, json=data)

    return r.json()


def make_token_refresh_request(client: Client, refresh_token: str):
    url = "http://127.0.0.1:8000/api/auth/token/refresh/"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "refresh": refresh_token
    }

    r = client.post(url, headers=headers, json=data)

    return r.json()


def make_events_request(client: Client, access_token: str | None = None):
    url = "http://127.0.0.1:8000/api/events/"
    headers = {
        "Content-Type": "application/json"
    }
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"

    r = client.get(url, headers=headers)

    r_json = r.json()
    if "count" in r_json:
        r_json = {"count": r.json()["count"]}

    return r_json


if __name__ == "__main__":
    with Client() as client:
        print(f"{make_events_request(client) = }")

        username = "dummy7"
        password = "12345678asdasd"

        r_json = make_register_request(client, username, password)
        print("make_register_request", r_json)
        refresh, access = r_json["refresh"], r_json["access"]
        
        print(f"{make_events_request(client, access_token=access) = }")

        r_json = make_login_request(client, username, password)
        print("make_login_request", r_json)
        refresh, access = r_json["refresh"], r_json["access"]
        
        print(f"{make_events_request(client, access_token=access) = }")

        access = make_token_refresh_request(client, refresh_token=refresh)["access"]
        print("make_token_refresh_request", access)
        
        print(f"{make_events_request(client, access_token=access) = }")

        print("make_logout_request", make_logout_request(client, refresh_token=refresh))

        r_json = make_token_refresh_request(client, refresh_token=refresh)
        print("make_token_refresh_request", r_json)
        
        print(f"{make_events_request(client, access_token=access) = }")











