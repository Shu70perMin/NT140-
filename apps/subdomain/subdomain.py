import argparse
import socket
import requests
from urllib.parse import urlparse
from threading import Thread, Semaphore
import re

# Console Colors
G = '\033[92m'  # green
Y = '\033[93m'  # yellow
R = '\033[91m'  # red
W = '\033[0m'   # white

def no_color():
    global G, Y, R, W
    G = Y = R = W = ''

def banner():
    print(f"{R}Subdomain Enumeration Tool{W}")
    print("A tool for enumerating subdomains using Search Engines, IP Mapping, and HTTP Status Check.")
    print("Usage: python subdomain.py -d <domain> [options]\n")
    print("Options:")
    print("  -d, --domain       Domain to enumerate subdomains (required)")
    print("  -t, --threads      Number of threads (default: 10)")
    print("  -e, --engines      Comma-separated list of search engines (e.g., google,yahoo,bing)")
    print("  -o, --output       Output file to save results")
    print("  -n, --no-color     Disable colored output")
    print("  -v, --verbose      Show results in realtime")
    print("  -s, --status       Check HTTP status codes for resolved subdomains")

def parse_args():
    parser = argparse.ArgumentParser(description="Subdomain Enumeration Tool")
    parser.add_argument('-d', '--domain', help="Domain to enumerate subdomains", required=True)
    parser.add_argument('-t', '--threads', help="Number of threads", type=int, default=10)
    parser.add_argument('-e', '--engines', help="Comma-separated list of search engines (e.g., google,yahoo,bing)")
    parser.add_argument('-o', '--output', help="Output file to save results")
    parser.add_argument('-n', '--no-color', help="Disable colored output", action='store_true')
    parser.add_argument('-v', '--verbose', help="Show results in realtime", action='store_true')
    parser.add_argument('-s', '--status', help="Check HTTP status codes for resolved subdomains", action='store_true')
    return parser.parse_args()

def fetch_subdomains_from_engines(domain, engines):
    print(f"{Y}Enumerating subdomains now for {domain}{W}")
    subdomains = set()
    engine_urls = {
        "google": f"https://google.com/search?q=site:{domain}",
        "yahoo": f"https://search.yahoo.com/search?p=site:{domain}",
        "bing": f"https://www.bing.com/search?q=site:{domain}",
        "baidu": f"https://www.baidu.com/s?wd=site:{domain}",
        "ask": f"http://www.ask.com/web?q=site:{domain}",
        "netcraft": f"https://searchdns.netcraft.com/?restriction=site+ends+with&host={domain}",
        "virustotal": f"https://www.virustotal.com/ui/domains/{domain}/subdomains",
        "threatcrowd": f"https://www.threatcrowd.org/searchApi/v2/domain/report/?domain={domain}",
        "dnsdumpster": f"https://dnsdumpster.com/",
        "ssl": f"https://crt.sh/?q=%.{domain}&output=json"
    }

    for engine in engines:
        print(f"{Y}[-] Searching now in {engine.capitalize()}..{W}")
        try:
            url = engine_urls.get(engine.lower())
            if not url:
                print(f"{R}Engine {engine} not supported{W}")
                continue
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                if engine.lower() == "virustotal":
                    data = response.json()
                    for item in data.get("data", []):
                        subdomains.add(item.get("id"))
                elif engine.lower() == "threatcrowd":
                    data = response.json()
                    subdomains.update(data.get("subdomains", []))
                elif engine.lower() == "ssl":
                    data = response.json()
                    for entry in data:
                        subdomains.update(entry["name_value"].split('\n'))
                else:
                    subdomains.update(set(re.findall(r"[a-zA-Z0-9.-]+\\." + domain, response.text)))
        except Exception as e:
            print(f"{R}Error fetching from {engine}: {e}{W}")
    return subdomains

def resolve_subdomains(subdomains, threads_count):
    resolved_ips = {}
    lock = Semaphore(1)
    threads = []

    for subdomain in subdomains:
        t = Thread(target=resolve_and_store, args=(subdomain, resolved_ips, lock))
        threads.append(t)
        t.start()

        if len(threads) >= threads_count:
            for t in threads:
                t.join()
            threads = []

    for t in threads:
        t.join()

    return resolved_ips

def resolve_and_store(subdomain, resolved_ips, lock):
    try:
        ip = socket.gethostbyname(subdomain)
        lock.acquire()
        resolved_ips[subdomain] = ip
        lock.release()
        print(f"{G}{subdomain} -> {ip}{W}")
    except socket.gaierror:
        pass

def check_http_status(resolved_ips):
    print(f"{Y}Checking HTTP status codes for resolved subdomains:{W}")
    status_results = {}
    for subdomain, ip in resolved_ips.items():
        url = f"http://{subdomain}"
        try:
            response = requests.get(url, timeout=5)
            status_results[subdomain] = response.status_code
            print(f"{G}{url} -> HTTP {response.status_code}{W}")
        except requests.RequestException as e:
            print(f"{R}{url} -> Error: {e}{W}")
    return status_results

def main():
    args = parse_args()
    if args.no_color:
        no_color()
    banner()

    domain = args.domain
    threads_count = args.threads
    output_file = args.output
    verbose = args.verbose

    engines = args.engines.split(',') if args.engines else [
        "google", "yahoo", "bing", "baidu", "ask",
        "netcraft", "virustotal", "threatcrowd", "dnsdumpster", "ssl"
    ]

    # Fetch subdomains
    subdomains = fetch_subdomains_from_engines(domain, engines)

    if not subdomains:
        print(f"{R}No subdomains found for {domain}{W}")
        return

    # Resolve subdomains
    resolved_ips = resolve_subdomains(subdomains, threads_count)

    # Check HTTP status codes if requested
    if args.status:
        check_http_status(resolved_ips)

    # Save results if output file is provided
    if output_file:
        print(f"{Y}Saving results to {output_file}{W}")
        with open(output_file, 'w') as f:
            for subdomain, ip in resolved_ips.items():
                f.write(f"{subdomain} -> {ip}\n")

    print(f"{G}Done. Found {len(resolved_ips)} subdomains.{W}")

if __name__ == "__main__":
    main()




