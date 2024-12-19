from extras.scripts import *

from virtualization.models import VirtualMachine
from virtualization.choices import VirtualMachineStatusChoices
from tenancy.models import Tenant

from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.worksheet.table import Table, TableStyleInfo

import datetime
import os

# --------------------

filename = "NetboxOut_" + str(datetime.datetime.now().strftime("%Y-%m")) + '.xlsx'
savePath = os.path.join('/opt/netbox/netbox/media',filename)

# ___VM attributes___
# Choices are: _name, bookmarks, cluster, cluster_id, comments, config_template, config_template_id, contacts, created, \
#  custom_field_data, description, device, device_id, disk, id, images, interface_count, interfaces, journal_entries, \
#  last_updated, local_context_data, memory, name, platform, platform_id, primary_ip4, primary_ip4_id, primary_ip6, \
#  primary_ip6_id, role, role_id, serial, services, site, site_id, status, subscriptions, tagged_items, tags, tenant, \
#  tenant_id, vcpus, virtual_disk_count, virtualdisks

# --------------------

class VM:
    def __init__(self, name, tenant, cores, ram, storage):
        self.name = name
        self.tenant = tenant
        self.cores = cores
        self.ram = ram
        self.storage = storage
    def get_name(self):
        return self.name
    def get_tenant(self):
        return self.tenant
    def get_cores(self):
        return self.cores
    def get_ram(self):
        return self.ram
    def get_storage(self):
        return self.storage

class TenantCalc:
    def __init__(self, id, name, cores, ram, storage):
        self.id = id
        self.name = name
        self.cores = cores
        self.ram = ram
        self.storage = storage
    def get_id(self):
        return self.id
    def get_name(self):
        return self.name
    def get_cores(self):
        return self.cores
    def set_cores(self, cores):
        self.cores = cores
    def get_ram(self):
        return self.ram
    def set_ram(self, ram):
        self.ram = ram
    def get_storage(self):
        return self.storage
    def set_storage(self, storage):
        self.storage = storage

class ExportAllVMResourcesToCSV(Script):
    class Meta:
        name = "Export All Tenant Resources to .csv"
        description = "Check assigned hardware resources of all active VMs and export them to a .csv file sorted by tenant."
        commit_default = False

    # --------------------

    def run(self, data, commit):

        # tenants to list - id, name, cores, ram, storage
        tenants = []
        for tenant in Tenant.objects.all():
            tenants.append(TenantCalc(tenant.id, tenant.name, 0, 0, 0))
        #tenants = tenants.reverse() # reverse order -> NOPE, breaks typing ^^
        tenants = list(reversed(tenants))
        self.log_info(f"Tenants collected.")

        # iterate through active VMs and add resources to tenants
        for vm in VirtualMachine.objects.filter(status=VirtualMachineStatusChoices.STATUS_ACTIVE):
            for tenant in tenants:
                if vm.tenant_id == tenant.get_id():
                    tenant.set_cores(tenant.get_cores()+vm.vcpus)
                    tenant.set_ram(tenant.get_ram()+(vm.memory/1024))
                    tenant.set_storage(tenant.get_storage()+(vm.disk/1000))
        self.log_info(f"VMs & resources collected.")

        # Setup Workbook for Excel output, add data
        wb = Workbook()
        ws = wb.active
        headRow = ["Tenant", "ID", "vCores (per core)", "RAM (per GB)", "Storage (per GB)"]
        ws.append(headRow)
        for tenant in tenants:
            ws.append([tenant.get_name(),tenant.get_id(),tenant.get_cores(),tenant.get_ram(),tenant.get_storage()])

        # Change column widths
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            adjusted_width = (max_length + 2) * 1.3
            ws.column_dimensions[column_letter].width = adjusted_width

        # Head row style & sheet name
        ft = Font(name='Calibri', size=12, bold=True)
        headRowx = "A1:E1"
        for row in ws[headRowx]:
            for cell in row:
                cell.font = ft
        sheetName = f"Tenant Resources {datetime.datetime.now().strftime("%d.%m.%Y")}"
        ws.title = sheetName

        # [UPDATE] format as table // https://openpyxl.readthedocs.io/en/3.1.3/worksheet_tables.html
        tab = Table(displayName="Tenants", ref=f"A1:E{len(tenants)+1}")
        # Add a default style with striped rows and banded columns
        style = TableStyleInfo(name="TableStyleMedium9", showFirstColumn=False,
                               showLastColumn=False, showRowStripes=True, showColumnStripes=False)
        tab.tableStyleInfo = style
        ws.add_table(tab)

        # Save to file
        #savePath = f'/opt/netbox/NetboxOut_{datetime.datetime.now().strftime("%Y.%m")}.xlsx'
        self.log_info(f"Saving file: {savePath}")
        wb.close()
        wb.save(savePath)
        self.log_success(f"File exported successfully.")

        # Export to SFTP ?
        # https://stackoverflow.com/questions/33751854/upload-file-via-sftp-with-python#73432631
        # import paramiko
        #
        # with paramiko.SSHClient() as ssh:
        #     ssh.load_system_host_keys()
        #     ssh.connect(host, username=username, password=password)
        #     sftp = ssh.open_sftp()
        #     sftp.chdir('public')
        #     sftp.put('C:\Users\XXX\Dropbox\test.txt', 'test.txt')
