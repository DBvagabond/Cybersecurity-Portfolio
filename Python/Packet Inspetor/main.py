from scapy.all import sniff, IP, TCP, UDP
import logging
from rich.console import Console
from rich.table import Table

# Setup logging
logging.basicConfig(filename='packets.log', level=logging.INFO, format='%(message)s')
console = Console()

def packet_callback(packet, protocol):
    if protocol == "tcp" and packet.haslayer(TCP):
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        src_port = packet[TCP].sport
        dst_port = packet[TCP].dport
        packet_info = f"TCP Packet: {src_ip}:{src_port} --> {dst_ip}:{dst_port}"
    elif protocol == "udp" and packet.haslayer(UDP):
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        src_port = packet[UDP].sport
        dst_port = packet[UDP].dport
        packet_info = f"UDP Packet: {src_ip}:{src_port} --> {dst_ip}:{dst_port}"
    else:
        return  # Ignore other protocols

    # Display with Rich
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Source IP")
    table.add_column("Destination IP")
    table.add_column("Source Port")
    table.add_column("Destination Port")
    table.add_row(src_ip, dst_ip, str(src_port), str(dst_port))
    console.print(table)

    # Log packet details to file
    logging.info(packet_info)

# Input validation for protocol selection
def get_valid_protocol():
    valid_protocols = ['tcp', 'udp']
    while True:
        protocol = input("Enter protocol to sniff (tcp/udp): ").lower()
        if protocol in valid_protocols:
            return protocol
        else:
            print("Invalid protocol! Please enter either 'tcp' or 'udp'.")
