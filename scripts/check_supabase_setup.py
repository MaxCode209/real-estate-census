"""Check Supabase connection and provide troubleshooting steps."""
import requests
import sys

def check_supabase_project():
    """Check if Supabase project is accessible."""
    hostname = "db.naixizrmldynltbaioem.supabase.co"
    
    print("Checking Supabase project setup...")
    print(f"Hostname: {hostname}\n")
    
    # Check 1: DNS Resolution
    import socket
    try:
        ip = socket.gethostbyname(hostname)
        print(f"✓ DNS resolves to: {ip}")
    except socket.gaierror:
        print("✗ DNS resolution failed")
        print("  → Project might still be provisioning")
        print("  → Check Supabase dashboard for project status")
        return False
    
    # Check 2: Port connectivity
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    result = sock.connect_ex((hostname, 5432))
    sock.close()
    
    if result == 0:
        print("✓ Port 5432 is accessible")
    else:
        print("✗ Port 5432 is not accessible")
        print("  → This could mean:")
        print("    - Project is still setting up")
        print("    - Your IP needs to be whitelisted")
        print("    - Firewall is blocking the connection")
    
    print("\nNext steps:")
    print("1. Go to https://supabase.com/dashboard")
    print("2. Check your project status (should be 'Active')")
    print("3. Go to Settings → Database → Connection string")
    print("4. Verify you're using 'Session mode'")
    print("5. Make sure password has no brackets [] in the connection string")
    print("6. Check if IP whitelisting is enabled (Settings → Database)")
    
    return result == 0

if __name__ == '__main__':
    check_supabase_project()

