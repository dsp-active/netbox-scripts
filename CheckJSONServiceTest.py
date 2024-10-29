from extras.scripts import *

from virtualization.models import VirtualMachine
from virtualization.choices import VirtualMachineStatusChoices
from ipam.models import Service

#from jsonschema import validate

#--------------------

class CheckJSONServiceTest(Script):
    class Meta:
        name = "Test the JSON Config of chosen services"
        description = "Use the JSON Schema library to check the JSON content of the config custom field."
        commit_default = False

    vm_choice = MultiObjectVar(
        description = "Choose a VM",
        model = VirtualMachine,
        required = True,
        query_params={
            "status": VirtualMachineStatusChoices.STATUS_ACTIVE
        }
    )

    #--------------------

    def run(self, data, commit):

        # get & check services
        for vm in data['vm_choice']:
            
            services = Service.objects.filter(virtual_machine=vm.id)
            
            for s in services:
                self.log_success(f"{vm} has the following service: {s}")
                s.get_custom_fields()

            # formatting
            self.log_info(f"--------------------------")
