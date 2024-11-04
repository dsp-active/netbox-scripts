from extras.scripts import *

from virtualization.models import VirtualMachine
from virtualization.choices import VirtualMachineStatusChoices
from ipam.models import Service

from jsonschema import validate
import json

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
        description = "Use the JSON Schema library to check the JSON config of every VM available."
        commit_default = False

    def run(self, data, commit):

        for vm in VirtualMachine.objects.filter(status=VirtualMachineStatusChoices.STATUS_ACTIVE):
            # get all services that match the chosen vm
            services = Service.objects.filter(virtual_machine=vm.id)

            for s in services:
                # list services
                self.log_info(f"{vm} has the following service: {s}")

                # Check custom data, get config & validate against scheme
                customData = s.get_custom_fields()
                customDataX = ", ".join("=".join((str(k), str(v))) for k, v in customData.items())
                customDataX = ("{" + (customDataX.split('{')[1]).split('}')[0] + "}").replace("'", '"')
                self.log_info(f"json Config: {customDataX}")
                cfg = json.loads(customDataX)

                # validate against scheme
                try:
                    validate(instance=cfg, schema=schema)
                    self.log_success(f"Config stimmt mit den Vorgaben überein.")
                except Exception as e:
                    self.log_warning(f"Config ist fehlerhaft! Bitte prüfen!\n{e}")

                # formatting
                self.log_info(f"--------------------------")
