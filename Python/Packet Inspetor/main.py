from scapy.all import sniff, IP, TCP, UDP, ICMP
import logging
from rich.console import Console
from rich.table import Table
from rich import box
from datetime import datetime

# Setup logging
logging.basicConfig(filename='packets.log', level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
console = Console()

# Packet processing callback
def packet_callback(packet, protocol):
    packet_info = None
    table_color = "white"
    
    if protocol == "tcp" and packet.haslayer(TCP):
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        src_port = packet[TCP].sport
        dst_port = packet[TCP].dport
        packet_info = f"TCP Packet: {src_ip}:{src_port} --> {dst_ip}:{dst_port}"
        table_color = "cyan"
    elif protocol == "udp" and packet.haslayer(UDP):
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        src_port = packet[UDP].sport
        dst_port = packet[UDP].dport
        packet_info = f"UDP Packet: {src_ip}:{src_port} --> {dst_ip}:{dst_port}"
        table_color = "green"
    elif protocol == "icmp" and packet.haslayer(ICMP):
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        packet_info = f"ICMP Packet: {src_ip} --> {dst_ip}"
        table_color = "yellow"
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
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        table.add_row(
            timestamp,
            src_ip, 
            dst_ip, 
            str(src_port) if 'src_port' in locals() else "N/A",
            str(dst_port) if 'dst_port' in locals() else "N/A",
            style=table_color
        )
        console.print(table)

    # Log packet details to file
    logging.info(packet_info)

# Input validation for protocol selection
def get_valid_protocol():
    valid_protocols = ['tcp', 'udp', 'icmp']
    while True:
        protocol = input("Enter protocol to sniff (tcp/udp/icmp): ").lower()
        if protocol in valid_protocols:
            return protocol
        else:
            print("Invalid protocol! Please enter either 'tcp', 'udp', or 'icmp'.")

# Input validation for packet count
def get_valid_packet_count():
    while True:
        try:
            count = int(input("Enter number of packets to capture: "))
            if count > 0:
                return count
            else:
                print("Please enter a positive number.")
        except ValueError:
            print("Invalid input! Please enter a valid number.")

def main():
    # Get user inputs
    protocol = get_valid_protocol()
    packet_count = get_valid_packet_count()

    try:
        # Start sniffing packets
        print(f"Sniffing {packet_count} {protocol.upper()} packets...")
        sniff(prn=lambda packet: packet_callback(packet, protocol), count=packet_count)
    except KeyboardInterrupt:
        print("\nSniffing interrupted by user. Exiting...")

if __name__ == "__main__":
    main()
