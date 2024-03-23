# This is a sample Python script.
import os

import requests
from dotenv import load_dotenv
import time

from logging_facility import configure_logging

load_dotenv()


class HttpError(Exception):
    def __init__(self, message, errors=None):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)

        # Now for your custom code...
        self.errors = errors


def get_public_ip():
    response = requests.get('https://api.ipify.org?format=json')
    if response.status_code != 200:
        raise HttpError(f"Could not get IP number, HTTP service returned {response.status_code}")
    return response.json()["ip"]


def read_last_ip() -> str | None:
    try:
        with open("last.ip", "r") as last_ip_file:
            read = last_ip_file.read()
            return read
    except FileNotFoundError:
        return None


def store_last_ip(last_ip_: str) -> int:
    logger.info(f"Updating store with new IP {last_ip_}")
    try:
        with open("last.ip", "w") as last_ip_file:
            return last_ip_file.write(last_ip_)
    except Exception as e:
        logger.exception("Problem writing to file \"last.ip\" ", e)


def update_duckdns_ip(domain_: str, public_ip_: str, token_: str):
    logger.info(f"Updating \"{domain_}\" with new IP {public_ip_}")
    response = requests.get(
        f"https://www.duckdns.org/update?domains={domain_}&token={token_}[&ip={public_ip_}]")
    if response.status_code != 200:
        raise HttpError(f"Could not update IP number, HTTP service returned {response.status_code}")


logger = configure_logging()


def handle_update(domain_: str, token_: str):
    last_ip = read_last_ip()
    public_ip = get_public_ip()
    if last_ip is None:
        logger.debug(f"First run, no previous IP found")
        store_last_ip(public_ip)
        update_duckdns_ip(domain_, public_ip, token_)
    else:
        if public_ip != last_ip:
            logger.info(f"Last known IP address {last_ip} does not match present one {public_ip}")
            update_duckdns_ip(domain_, public_ip, token_)
        else:
            logger.info(f"No action, IP matches {public_ip}")


if __name__ == '__main__':
    start = time.time_ns()
    logger.debug("Updater started")

    domain = os.getenv("DUCKDNS_DOMAIN")
    token = os.getenv("DUCKDNS_TOKEN")

    handle_update(domain, token)

    elapsed = time.time_ns() - start
    logger.debug("Updater finished in %d milliseconds", elapsed / 1_000_000)
