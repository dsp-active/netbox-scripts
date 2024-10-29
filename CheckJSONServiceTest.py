from extras.scripts import *

from virtualization.models import VirtualMachine
from virtualization.choices import VirtualMachineStatusChoices
from ipam.models import Service

from jsonschema import validate

#--------------------

schema = {
    "type": "object",
    "properties": {
        "app": {"type": "string", "minLength": 1},
        "user": {"type": "string", "minLength": 1}
    },
    "required": ["app"],
    "additionalProperties": False,
}

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
        
        for vm in data['vm_choice']:
            # get all services that match the chosen vm
            services = Service.objects.filter(virtual_machine=vm.id)
            
            for s in services:
                # list services
                self.log_info(f"{vm} has the following service: {s}")
                
                # Check custom data, get config & validate against scheme
                customData = s.get_custom_fields()
                self.log_info(f"custom data: {customData} // of type {customData.type}")
                
                
                # formatting
                self.log_info(f"--------------------------")
