from scapy.all import sniff, IP, TCP, UDP, ICMP, wrpcap
import logging
from rich.console import Console
from rich.table import Table
from rich import box
from datetime import datetime, timedelta
from collections import defaultdict

# Get timestamp for filenames
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

# Setup logging with timestamped filename
log_filename = f'packets_{timestamp}.log'
logging.basicConfig(filename=log_filename, level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
console = Console()

# List to store captured packets
captured_packets = []

# Store data for suspicious activity detection
ip_activity = defaultdict(list)  # Track IPs and their port usage
icmp_count = defaultdict(int)    # Track ICMP packet count per source
suspicious_ips = set()           # Set of flagged suspicious IPs

# Thresholds for detecting suspicious activity
PORT_SCAN_THRESHOLD = 10  # Multiple ports accessed within a short period
ICMP_FLOOD_THRESHOLD = 100  # Number of ICMP requests in a short period
TRAFFIC_SPIKE_THRESHOLD = 50  # Number of packets from an IP in a short period

# Packet processing callback
def packet_callback(packet, protocol):
    packet_info = None
    table_color = "white"
    
    # Check if the packet has an IP layer
    if not packet.haslayer(IP):
        return  # Ignore packets without IP layer (e.g., ARP packets)

    src_ip = packet[IP].src
    dst_ip = packet[IP].dst
    packet_time = datetime.now()

    if protocol == "tcp" and packet.haslayer(TCP):
        src_port = packet[TCP].sport
        dst_port = packet[TCP].dport
        packet_info = f"TCP Packet: {src_ip}:{src_port} --> {dst_ip}:{dst_port}"
        table_color = "cyan"
        detect_port_scanning(src_ip, src_port, packet_time)  # Check for port scanning
    elif protocol == "udp" and packet.haslayer(UDP):
        src_port = packet[UDP].sport
        dst_port = packet[UDP].dport
        packet_info = f"UDP Packet: {src_ip}:{src_port} --> {dst_ip}:{dst_port}"
        table_color = "green"
    elif protocol == "icmp" and packet.haslayer(ICMP):
        packet_info = f"ICMP Packet: {src_ip} --> {dst_ip}"
        table_color = "yellow"
        detect_icmp_flooding(src_ip)  # Check for ICMP flooding
    else:
        return  # Ignore other protocols

    # Display with Rich
    if packet_info:
        table = Table(show_header=True, header_style="bold magenta", box=box.SQUARE)
        table.add_column("Timestamp", style="dim")
        table.add_column("Source IP")
        table.add_column("Destination IP")
        table.add_column("Source Port")
        table.add_column("Destination Port")
        
        packet_timestamp = packet_time.strftime('%Y-%m-%d %H:%M:%S')
        table.add_row(
            packet_timestamp,
            src_ip, 
            dst_ip, 
            str(src_port) if 'src_port' in locals() else "N/A",
            str(dst_port) if 'dst_port' in locals() else "N/A",
            style=table_color
        )
        console.print(table)

    # Log packet details to file
    logging.info(packet_info)
    
    # Store packet for exporting
    captured_packets.append(packet)

# Detect suspicious port scanning activity
def detect_port_scanning(ip, port, timestamp):
    ip_activity[ip].append((port, timestamp))
    recent_ports = [p for p, t in ip_activity[ip] if timestamp - t < timedelta(seconds=10)]  # Last 10 seconds
    if len(set(recent_ports)) >= PORT_SCAN_THRESHOLD:
        log_suspicious_activity(f"Suspicious activity detected: Port scanning from {ip}")

# Detect suspicious ICMP flooding
def detect_icmp_flooding(ip):
    icmp_count[ip] += 1
    if icmp_count[ip] > ICMP_FLOOD_THRESHOLD:
        log_suspicious_activity(f"Suspicious activity detected: ICMP flood coming from {ip}")

# Log suspicious activity
def log_suspicious_activity(message):
    console.print(f"[bold red]{message}[/bold red]")
    logging.warning(message)
    suspicious_ips.add(message)

# Input validation for protocol selection
def get_valid_protocol():
    valid_protocols = ['tcp', 'udp', 'icmp']
    while True:
        protocol = input("Enter protocol to sniff (tcp/udp/icmp): ").lower()
        if protocol in valid_protocols:
            return protocol
        else:
            print("Invalid protocol! Please enter either 'tcp', 'udp', or 'icmp'.")

# Input validation for packet count or continuous sniffing
def get_packet_count_or_continuous():
    while True:
        user_input = input("Enter number of packets to capture or 'c' for continuous sniffing: ").strip()
        if user_input.lower() == 'c':
            return None  # Continuous sniffing mode
        try:
            count = int(user_input)
            if count > 0:
                return count
            else:
                print("Please enter a positive number.")
        except ValueError:
            print("Invalid input! Please enter a valid number or 'c' for continuous mode.")

# Function to export packets to a .pcap file with timestamped filename
def export_packets_to_pcap():
    pcap_filename = f'captured_packets_{timestamp}.pcap'
    if captured_packets:
        wrpcap(pcap_filename, captured_packets)
        print(f"Packets saved to {pcap_filename}")
    else:
        print("No packets to save.")

def main():
    # Get user inputs
    protocol = get_valid_protocol()
    packet_count = get_packet_count_or_continuous()  # Either specific count or continuous mode

    try:
        # Start sniffing packets
        if packet_count is None:
            print("Sniffing continuously. Press Ctrl+C to stop...")
            sniff(prn=lambda packet: packet_callback(packet, protocol))  # No count, sniff until interrupted
        else:
            print(f"Sniffing {packet_count} {protocol.upper()} packets...")
            sniff(prn=lambda packet: packet_callback(packet, protocol), count=packet_count)
        
        # Export captured packets to pcap file
        export_packets_to_pcap()
    
    except KeyboardInterrupt:
        print("\nSniffing interrupted by user. Exiting...")
        export_packets_to_pcap()  # Save packets even if interrupted

if __name__ == "__main__":
    main()
