from extras.scripts import *

from ipam.models import IPAddress
from ipam.choices import IPAddressStatusChoices

#--------------------

class IPBulkCheckTest(Script):
    class Meta:
        name = "IP Bulk Check Tester"
        description = "Test every IP address and its corresponding dns-name against each other"
        commit_default = False

    def run(self, data, commit):

        for address in IPAddress.objects.filter(status=IPAddressStatusChoices.STATUS_ACTIVE):
            if address.dns_name is not None and address.dns_name != "":
                self.log_success(f"{address.dns_name} belongs to {address}")
            else:
                self.log_warning(f"{address} does not have a set DNS name.")
