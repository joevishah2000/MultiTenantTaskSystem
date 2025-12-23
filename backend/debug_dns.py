import socket
import sys

hostname = "db.pvsxlswxanzxiymloohi.supabase.co"

print(f"Attempting to resolve {hostname}...")

try:
    # Try generic resolution
    infos = socket.getaddrinfo(hostname, 5432)
    print("SUCCESS: socket.getaddrinfo returned:")
    for family, type, proto, canonname, sockaddr in infos:
        print(f"  Family: {family}, Addr: {sockaddr}")
except Exception as e:
    print(f"ERROR: generic getaddrinfo failed: {e}")

print("-" * 20)

try:
    # Try IPv4 only
    infos = socket.getaddrinfo(hostname, 5432, family=socket.AF_INET)
    print("SUCCESS: IPv4 resolution returned:")
    for family, type, proto, canonname, sockaddr in infos:
        print(f"  Family: {family}, Addr: {sockaddr}")
except Exception as e:
    print(f"ERROR: IPv4 getaddrinfo failed: {e}")

print("-" * 20)

try:
    # Try IPv6 only
    infos = socket.getaddrinfo(hostname, 5432, family=socket.AF_INET6)
    print("SUCCESS: IPv6 resolution returned:")
    for family, type, proto, canonname, sockaddr in infos:
        print(f"  Family: {family}, Addr: {sockaddr}")
except Exception as e:
    print(f"ERROR: IPv6 getaddrinfo failed: {e}")
