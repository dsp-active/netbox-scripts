from extras.scripts import *

from virtualization.models import VirtualMachine
from virtualization.choices import VirtualMachineStatusChoices

#--------------------

class VMCostTest(Script):
    class Meta:
        name = "Test Calculation of VM ressource costs"
        description = "Calculate a given VMs cost based on its used ressources like vCores and RAM."
        commit_default = False
        
    vm_choice = MultiObjectVar(
        description = "Choose a VM",
        model = VirtualMachine,
        required = True,
        query_params={
            "status": VirtualMachineStatusChoices.STATUS_ACTIVE
        }
    )
    
    # there is no Float or DecimalVar for whatever reason~
    vcore_price = StringVar(
        description = "Cost for a single assigned vCore in the following format: X.XX",
        default = "1.00",
        min_length = 4,
        regex = "^[0-9]+[.]{1}[0-9]{2}" # starts with 1 or more numbers followed by 1 dot and 2 more numbers
    )

    def run(self, data, commit):
        
        # regex to float
        vcore_price = float(data['vcore_price'])
        
        # cost calc
        for vm in data['vm_choice']:
            if vm.vcpus is not None and vm.vcpus != "":
                self.log_info(f"{vm} has {vm.vcpus} vCores assigned to it.")
                calc = "{:.2f}".format(float(vcore_price * vm.vcpus))
                self.log_success(f"{vm} therefore costs {calc}€ per month.")
            else:
                self.log_warning(f"{vm} does not have a set amount of vCores.")
        
        # formatting
        self.log_info(f"--------------------------")
