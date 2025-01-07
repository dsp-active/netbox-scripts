from extras.scripts import *

from virtualization.models import VirtualMachine
from virtualization.choices import VirtualMachineStatusChoices
from tenancy.models import Tenant

from openpyxl import Workbook
from openpyxl.styles import Font, colors
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

class Application:
     def __init__(self, tenant, name, cores, ram, storage):
         self.tenant = tenant
         self.name = name
         self.cores = cores
         self.ram = ram
         self.storage = storage
     def get_tenant(self):
         return self.tenant
     def set_tenant(self,tenant):
         self.tenant = tenant
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
     def set_storage(self,storage):
         self.storage = storage

class TenantCalc:
    def __init__(self, id, name):
        self.id = id
        self.name = name
    def get_id(self):
        return self.id
    def get_name(self):
        return self.name

class ExportAllVMResourcesToXLSX(Script):
    class Meta:
        name = "Export All Tenant Resources to .xlsx"
        description = "Check assigned hardware resources of all active VMs and export them to an Excel file sorted by tenant."
        commit_default = False

    # --------------------

    def run(self, data, commit):

        # tenants to list
        tenants = []
        for tenant in Tenant.objects.all():
            tenants.append(TenantCalc(tenant.id, tenant.name))
        #tenants = tenants.reverse() # reverse order -> NOPE, breaks typing ^^
        tenants = list(reversed(tenants))
        self.log_info(f"Tenants collected.")

        # iterate through active VMs and add resources to tenant + application pairs
        applications = []
        for vm in VirtualMachine.objects.filter(status=VirtualMachineStatusChoices.STATUS_ACTIVE):
            customData = vm.get_custom_fields()
            app = ", ".join("=".join((str(k), str(v))) for k, v in customData.items())
            app = app.split('Application=')[1].split(',')[0]
            for tenant in tenants:
                if vm.tenant_id == tenant.get_id():
                    applications.append(Application(tenant.get_name(), app, vm.vcpus, round(vm.memory/1024), round(vm.disk/1000)))
        self.log_info(f"Resources collected.")

        # setup Workbook for Excel output & add data
        wb = Workbook()
        ws = wb.active
        headRow = ["Tenant", "Application", "vCores (per core)", "RAM (per GB)", "Storage (per GB)"]
        ws.append(headRow)
        for app in applications:
            ws.append([app.get_tenant(),app.get_name(),app.get_cores(),app.get_ram(),app.get_storage()])

        # last row + styling & mark functions as such to prevent errors
        emptyRow = ["", "", "", "", ""] # dumb but it looks better (:
        ws.append(emptyRow)
        bottomRow = ["Gesamt:", "", f"=SUBTOTAL(9,Tenants[vCores (per core)])", f"=SUBTOTAL(9,Tenants[RAM (per GB)])",
                     f"=SUBTOTAL(9,Tenants[Storage (per GB)])"]
        ws.append(bottomRow)
        lastRow = f"A{ws.max_row}:E{ws.max_row}"
        for row in ws[lastRow]:
            for cell in row:
                cell.font = Font(bold=True)
                if str(cell.value).startswith('='):
                    cell.data_type = 'f'

        # change column widths
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                if len(str(cell.value)) > max_length and not str(cell.value).startswith('='):
                    max_length = len(cell.value)
            adjusted_width = (max_length + 2) * 1.2
            ws.column_dimensions[column_letter].width = adjusted_width

        # head row style & sheet name
        ft = Font(name='Calibri', size=12, bold=True, color="#ffece9e4") # color = argb hex value
        headRowx = "A1:E1"
        for row in ws[headRowx]:
            for cell in row:
                cell.font = ft
        sheetName = f"Tenant Resources {datetime.datetime.now().strftime("%d.%m.%Y")}"
        ws.title = sheetName

        # [UPDATE] format as table // https://openpyxl.readthedocs.io/en/3.1.3/worksheet_tables.html
        tab = Table(displayName="Tenants", ref=f"A1:E{len(applications)+1}")
        style = TableStyleInfo(name="TableStyleMedium9", showFirstColumn=False,
                               showLastColumn=False, showRowStripes=True, showColumnStripes=False)
        tab.tableStyleInfo = style
        ws.add_table(tab)

        # save to file
        self.log_info(f"Saving file: {savePath}")
        wb.close()
        wb.save(savePath)
        self.log_success(f"File exported successfully.")

        # export to SFTP ?
        # https://stackoverflow.com/questions/33751854/upload-file-via-sftp-with-python#73432631
        # import paramiko
        #
        # with paramiko.SSHClient() as ssh:
        #     ssh.load_system_host_keys()
        #     ssh.connect(host, username=username, password=password)
        #     sftp = ssh.open_sftp()
        #     sftp.chdir('public')
        #     sftp.put('C:\Users\XXX\Dropbox\test.txt', 'test.txt')
