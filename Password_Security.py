#!/usr/bin/env python3
"""
Educational Network Vulnerability Scanner Outline
This is a basic framework demonstrating vulnerability scanning concepts.
FOR EDUCATIONAL PURPOSES ONLY - Use only on networks you own or have permission to test.
"""

import socket
import threading
import subprocess
import time
from datetime import datetime
import json

class NetworkVulnScanner:
    def __init__(self):
        self.target_host = None
        self.target_ports = []
        self.scan_results = {}
        self.vulnerabilities = []
        
    def set_target(self, host, port_range=None):
        """Set the target host and port range for scanning"""
        self.target_host = host
        if port_range:
            start, end = port_range
            self.target_ports = list(range(start, end + 1))
        else:
            # Common ports if no range specified
            self.target_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995]
    
    def ping_host(self):
        """Check if target host is reachable"""
        import platform
        
        # Skip ping for localhost - it should always be reachable
        if self.target_host in ['127.0.0.1', 'localhost']:
            return True
            
        try:
            # Determine ping command based on OS
            system = platform.system().lower()
            if system == "windows":
                cmd = ['ping', '-n', '1', self.target_host]
            else:  # Linux/macOS/Unix
                cmd = ['ping', '-c', '1', self.target_host]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            print(f"Ping result: {result.returncode}")  # Debug output
            return result.returncode == 0
        except Exception as e:
            print(f"Ping failed with exception: {e}")  # Debug output
            return False
    
    def port_scan(self, port):
        """Scan a single port"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((self.target_host, port))
            sock.close()
            
            if result == 0:
                service = self.identify_service(port)
                return {"port": port, "status": "open", "service": service}
            else:
                return {"port": port, "status": "closed", "service": None}
        except:
            return {"port": port, "status": "filtered", "service": None}
    
    def identify_service(self, port):
        """Basic service identification by port number"""
        common_ports = {
            21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
            53: "DNS", 80: "HTTP", 110: "POP3", 143: "IMAP",
            443: "HTTPS", 993: "IMAPS", 995: "POP3S"
        }
        return common_ports.get(port, "Unknown")
    
    def banner_grab(self, port):
        """Attempt to grab service banner for version detection"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((self.target_host, port))
            
            # Send a generic request
            sock.send(b"GET / HTTP/1.1\r\nHost: " + self.target_host.encode() + b"\r\n\r\n")
            banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
            sock.close()
            return banner
        except:
            return None
    
    def check_common_vulnerabilities(self):
        """Check for common vulnerabilities based on open ports and services"""
        vulnerabilities = []
        
        for port_info in self.scan_results.get('open_ports', []):
            port = port_info['port']
            service = port_info['service']
            
            # Example vulnerability checks
            if port == 21:  # FTP
                vulnerabilities.append({
                    "port": port,
                    "service": service,
                    "vulnerability": "Anonymous FTP Access",
                    "severity": "Medium",
                    "description": "FTP server may allow anonymous access"
                })
            
            elif port == 23:  # Telnet
                vulnerabilities.append({
                    "port": port,
                    "service": service,
                    "vulnerability": "Unencrypted Protocol",
                    "severity": "High",
                    "description": "Telnet transmits data in plaintext"
                })
            
            elif port == 80:  # HTTP
                banner = self.banner_grab(port)
                if banner and "Server:" in banner:
                    vulnerabilities.append({
                        "port": port,
                        "service": service,
                        "vulnerability": "Information Disclosure",
                        "severity": "Low",
                        "description": f"Server banner revealed: {banner[:100]}"
                    })
        
        return vulnerabilities
    
    def run_scan(self):
        """Execute the complete vulnerability scan"""
        print(f"Starting vulnerability scan of {self.target_host}")
        print(f"Scan started at: {datetime.now()}")
        
        # Step 1: Host discovery
        print("\n[1] Checking host availability...")
        if not self.ping_host():
            print(f"Host {self.target_host} appears to be unreachable via ping")
            print("Continuing with port scan anyway (host might block ICMP)...")
        else:
            print(f"Host {self.target_host} is reachable")
        
        # Step 2: Port scanning
        print(f"\n[2] Scanning {len(self.target_ports)} ports...")
        open_ports = []
        
        def scan_port(port):
            result = self.port_scan(port)
            if result['status'] == 'open':
                open_ports.append(result)
                print(f"Found open port: {port} ({result['service']})")
        
        # Multi-threaded port scanning
        threads = []
        for port in self.target_ports:
            thread = threading.Thread(target=scan_port, args=(port,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        self.scan_results['open_ports'] = open_ports
        
        # Step 3: Service enumeration
        print(f"\n[3] Enumerating services on {len(open_ports)} open ports...")
        for port_info in open_ports:
            banner = self.banner_grab(port_info['port'])
            if banner:
                port_info['banner'] = banner
                print(f"Banner for port {port_info['port']}: {banner[:50]}...")
        
        # Step 4: Vulnerability assessment
        print(f"\n[4] Checking for common vulnerabilities...")
        self.vulnerabilities = self.check_common_vulnerabilities()
        
        # Step 5: Generate report
        self.generate_report()
    
    def generate_report(self):
        """Generate a vulnerability scan report"""
        print("\n" + "="*60)
        print("VULNERABILITY SCAN REPORT")
        print("="*60)
        
        print(f"Target: {self.target_host}")
        print(f"Scan completed: {datetime.now()}")
        print(f"Open ports found: {len(self.scan_results.get('open_ports', []))}")
        print(f"Vulnerabilities found: {len(self.vulnerabilities)}")
        
        print("\nOPEN PORTS:")
        print("-" * 40)
        for port_info in self.scan_results.get('open_ports', []):
            print(f"Port {port_info['port']:>5}: {port_info['service']}")
        
        print("\nVULNERABILITIES:")
        print("-" * 40)
        for vuln in self.vulnerabilities:
            print(f"Port {vuln['port']}: {vuln['vulnerability']} ({vuln['severity']})")
            print(f"    Description: {vuln['description']}")
        
        # Save results to JSON file
        report_data = {
            "target": self.target_host,
            "scan_time": str(datetime.now()),
            "open_ports": self.scan_results.get('open_ports', []),
            "vulnerabilities": self.vulnerabilities
        }
        
        with open(f"scan_report_{self.target_host}_{int(time.time())}.json", "w") as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\nDetailed report saved to JSON file")

def main():
    """Main function to demonstrate scanner usage"""
    scanner = NetworkVulnScanner()
    
    # Example usage - scan localhost
    target = "127.0.0.1"  # Only scan localhost for safety
    port_range = (20, 100)  # Scan ports 20-100
    
    scanner.set_target(target, port_range)
    scanner.run_scan()

if __name__ == "__main__":
    print("Educational Network Vulnerability Scanner")
    print("WARNING: Only use on networks you own or have explicit permission to test")
    print("This tool is for learning purposes only")
    
    # Uncomment the line below to run the demo (localhost scan only)
main()