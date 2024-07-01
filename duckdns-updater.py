import os

import requests
from dotenv import load_dotenv
import time
import dns.resolver

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


def resolve_dns_to_ip(domain_name):
    try:
        result = dns.resolver.resolve(domain_name, 'A')
        ip_addresses = [ip.address for ip in result]
        logger.info(f"Resolved IPs {ip_addresses}")
        return ip_addresses
    except dns.resolver.NoAnswer:
        return f"No answer for {domain_name}"
    except dns.resolver.NXDOMAIN:
        return f"{domain_name} does not exist"
    except dns.resolver.Timeout:
        return f"Timeout while resolving {domain_name}"
    except dns.exception.DNSException as e:
        return f"Error resolving {domain_name}: {e}"



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


def update_duckdns_ip(domain_name: str, public_ip_: str, token_: str):
    logger.info(f"Updating \"{domain_name}\" with new IP {public_ip_}")
    response = requests.get(
        f"https://www.duckdns.org/update?domains={domain_name}&token={token_}&ip={public_ip_}")
    if response.status_code != 200:
        raise HttpError(f"Could not update IP number, HTTP service returned {response.status_code}")


logger = configure_logging()

def handle_update_file_cache(domain_name: str, domain_:str, token_: str):
    last_ip = read_last_ip()
    public_ip = get_public_ip()
    if last_ip is None:
        logger.debug(f"First run, no previous IP found")
        store_last_ip(public_ip)
        update_duckdns_ip(domain_name, public_ip, token_)
    else:
        if public_ip != last_ip:
            logger.info(f"Last known IP address {last_ip} does not match present one {public_ip}")
            update_duckdns_ip(domain_name, public_ip, token_)
            store_last_ip(public_ip)
        else:
            logger.info(f"No action, IP matches {public_ip}")

def handle_update_dns_compare(domain_name: str, domain_:str, token_: str):
    resolved_ips =  resolve_dns_to_ip(f"{domain_name}.{domain_}")
    public_ip = get_public_ip()
    if resolved_ips is None or len(resolved_ips) == 0:
        logger.debug(f"No IP resolved for address ${resolved_ips}, seting it up")
        update_duckdns_ip(domain_name, public_ip, token_)
    else:
        if public_ip not in resolved_ips:
            logger.info(f"Last known IP addresses {resolved_ips} do not contain present one {public_ip}")
            update_duckdns_ip(domain_name, public_ip, token_)
        else:
            logger.info(f"No change, IP matches {public_ip} contained in {resolved_ips}")


if __name__ == '__main__':
    start = time.time_ns()
    logger.debug("Updater started")

    domain = os.getenv("DUCKDNS_DOMAIN")
    domain_name = os.getenv("DUCKDNS_DOMAIN_NAME")
    token = os.getenv("DUCKDNS_TOKEN")

    handle_update_dns_compare(domain_name, domain, token)

    elapsed = time.time_ns() - start
    logger.debug("Updater finished in %d milliseconds", elapsed / 1_000_000)
