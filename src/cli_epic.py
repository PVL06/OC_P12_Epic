import requests


base_url = "http://127.0.0.1:8000/"


def login():
    url = base_url + "login"

    data = {
        "email": "epic@epic.com",
        "password": "epic&1234"
    }

    res = requests.post(url, json=data)
    print(res.json())


if __name__ == "__main__":
    login()
