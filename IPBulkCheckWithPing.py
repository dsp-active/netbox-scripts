from extras.scripts import *

from ipam.models import IPAddress
from ipam.choices import IPAddressStatusChoices

#from icmplib import ping

#--------------------

class IPBulkCheckWithPing(Script):
    class Meta:
        name = "IP x DNS Bulk Check with Ping"
        description = "Test every IP address and its assigned dns-name against each other using Ping"
        commit_default = False

    ip_choice = MultiObjectVar(
        description = "Choose one or more IP Addresses",
        model = IPAddress,
        required = True,
        query_params={
            "status": IPAddressStatusChoices.STATUS_ACTIVE
        }
    )

    def run(self, data, commit):

        self.log_info(f"{data['ip_choice']} ausgewählt.")

        for ip in data['ip_choice']:
            if ip.dns_name is not None and ip.dns_name != "":
                self.log_success(f"{ip.dns_name} belongs to {ip}")
            else:
                self.log_warning(f"{ip} does not have a set DNS name.")

    # def run(self, data, commit):

        # for address in IPAddress.objects.filter(status=IPAddressStatusChoices.STATUS_ACTIVE):
            # if address.dns_name is not None and address.dns_name != "":
                # self.log_info(f"Testing {address.dns_name} against {address} ...")
                
                # # test ping
                # check = ping(str(address.dns_name), count=3, interval=0.2, timeout=2, privileged=False)
                
                # # compare dns-ip to registered ip
                # if str(address.address) in str(check):
                    # self.log_success(f"Registered IP and DNS match.")
                # else:
                    # self.log_warning(f"Registered IP and DNS do NOT match!")
                
                # # check if ping was successful or not
                # if 'received: 0' in str(check):
                    # self.log.warning(f"Ping failed!")
                # else:
                    # self.log_success(f"Ping was successful.")
            # else:
                # self.log_warning(f"{address} does not have a set DNS name!")
