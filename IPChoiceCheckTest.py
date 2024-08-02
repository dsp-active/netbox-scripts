from extras.scripts import *

from ipam.models import IPAddress
from ipam.choices import IPAddressStatusChoices

#--------------------

class IPChoiceCheckTest(Script):
    class Meta:
        name = "IP Check Tester"
        description = "Test given IP addresses and its corresponding dns-name against each other"
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

        #ip = IPAddress.objects.get(address=data['ip_choice'])

        for ip in data['ip_choice']:
            if ip.dns_name is not None and ip.dns_name != "":
                self.log_success(f"{ip.dns_name} belongs to {ip}")
            else:
                self.log_warning(f"{ip} does not have a set DNS name.")
