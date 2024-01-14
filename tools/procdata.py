import re

def check_ip_address_type(ip):
   
   ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
   ipv6_pattern = r'^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$'
   onion_pattern = r'\S*?\.onion'


   if re.match(ipv4_pattern, ip):
      return "IPv4"
   elif re.match(ipv6_pattern, ip):
      return "IPv6"
   elif re.match(onion_pattern,ip):
      return "Onion"
   else:
      return "Invalid"
