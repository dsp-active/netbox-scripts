from extras.scripts import *

from ipam.models import IPAddress
from ipam.choices import IPAddressStatusChoices

from icmplib import ping

#--------------------

# needs to run "docker compose exec -u root netbox /opt/netbox/venv/bin/python -m pip install icmplib" first!

class IPBulkCheckWithPing(Script):
    class Meta:
        name = "IP x DNS Bulk Check + Ping"
        description = "Test every IP address and its corresponding dns-name against each other using Ping"
        commit_default = False

    def run(self, data, commit):

        for address in IPAddress.objects.filter(status=IPAddressStatusChoices.STATUS_ACTIVE):
            if address.dns_name is not None and address.dns_name != "":
                self.log_info(f"Testing {address.dns_name} @ {address} ...")
                try:
                    # send ping to dns
                    check = ping(str(address.dns_name), count=3, interval=0.2, privileged=False)
                    
                    # compare ip from dns controller to registered ip
                    if str(address.address) in str(check):
                        self.log_success(f"Registered IP and DNS match.")
                    else:
                        self.log_warning(f"Registered IP and DNS do NOT match!")
                    
                    # check if ping succeeded
                    if 'received: 0' in str(check):
                        self.log.warning(f"Ping failed!")
                    else:
                        self.log_success(f"Ping was successful.")
                else:
                    self.log.warning(f"No DNS entry found!")
            else:
                self.log_warning(f"{address} does not have a set DNS name!")
