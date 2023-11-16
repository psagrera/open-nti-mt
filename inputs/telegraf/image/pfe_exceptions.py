from lxml.builder import E
import lxml
import re
from datetime import datetime
import pprint
import pandas as pd
#import pickle
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import *
from jnpr.junos.utils.start_shell import StartShell
from jnpr.junos.utils.fs import FS
from jnpr.junos import Device

# xml specific
from lxml import etree
from lxml.builder import E
import lxml

import time
# third-party
import ncclient.transport.errors as NcErrors
import ncclient.operations.errors as TError
import json, ast

import concurrent.futures
import yaml


class AutoVivification(dict):
        """Implementation of perl's autovivification feature."""
        def __getitem__(self, item):
                try:
                        return dict.__getitem__(self, item)
                except KeyError:
                        value = self[item] = type(self)()
                        return value



def get_pfe_execption(i):

        regex = "(.*\w+\s+)DISC\(.*\)\s+(\d+\s)(.*)"
        now = datetime.now()
        dt_string = now.strftime("%d-%m-%Y %H:%M:%S")
        my_dict = AutoVivification()
        aft = []
        aft_list = []
        cred = read_credentials('credentials.yaml')
        dev = Device(host=i,user=cred[0]['username'],password=cred[0]['password'],port=22)
        dev.open()
        fpcs_aft = dev.rpc.get_chassis_inventory()
        # Before 21.4 the command "show pfe statistics exceptions" doesn't work from the cli in AFT cards
        aft_slot = fpcs_aft.xpath("//chassis/chassis-module[contains(./description,'MPC1')]/name//text()")
        if aft and len(aft_slot) <= 1:
                aft = ''.join(aft_slot).split()[1]
        # we have more than one AFT card
        else:
                aft_list = [x.split(' ')[-1] for x in aft_slot]        
        
        fpc_list_xml = dev.rpc.get_fpc_information()
        fpc_list = fpc_list_xml.xpath('//fpc[state="Online"]//slot//text()')
        for f in fpc_list:
                if f not in aft:
                        o_result = dev.rpc.cli("show pfe statistics exceptions fpc " + f)
                        for slot in o_result.xpath("//output//text()"):
                                tmp = re.findall(regex,str(slot))
                        for j in tmp:
                                if j[1] != "0 ":
                                        my_dict[i][f][dt_string][j[0].strip()] = j[1]
                else:
                        
                        if aft:
                                fpc_target = "fpc" + aft
                                try:        
                                        aft_excep = dev.rpc.request_pfe_execute(target=fpc_target,command="show jnh exceptions level terse inst 0")
                                except RpcError as rpc_err:
                                        print(rpc_err)
                                for aft_e in aft_excep.xpath("//output//text()"):
                                        tmp_aft = re.findall(regex,str(aft_e))

                                for j_aft in tmp_aft:
                                        my_dict[i][aft][dt_string][j_aft[0].strip()] = j_aft[1]
                        if aft_list:
                                for mpc in aft_list:
                                        fpc_target = "fpc" + aft
                                        try:        
                                                aft_excep = dev.rpc.request_pfe_execute(target=fpc_target,command="show jnh exceptions level terse inst 0")
                                        except RpcError as rpc_err:
                                                print(rpc_err)
                                        for aft_e in aft_excep.xpath("//output//text()"):
                                                tmp_aft = re.findall(regex,str(aft_e))
        
                                        for j_aft in tmp_aft:
                                                my_dict[i][aft][dt_string][j_aft[0].strip()] = j_aft[1]

        output = {
            key4: {
                (k1, k2, k3): v3[key4]
                for k1, v1 in my_dict.items()
                for k2, v2 in v1.items()
                for k3, v3 in v2.items()
                if key4 in v3
            }
            for key1, value1 in my_dict.items()
            for key2, value2 in value1.items()
            for key3, value3 in value2.items()
            for key4 in value3.keys()
        }
        lines = []
        for k, v in output.items():
            measurement = k.replace(' ', '_')
            for tags, field in v.items():
                device, slot, timestamp = tags
                tag_set = f'device={device},slot={slot}'
                field_set = f'value={field}'
                timestamp_ns = int(datetime.strptime(timestamp, '%d-%m-%Y %H:%M:%S').timestamp() * 10**9)
                line = f'{i}.{slot}.{measurement},{tag_set} {field_set} {timestamp_ns}'
                lines.append(line)       
        return lines

def read_credentials(file_path):

        with open(file_path, 'r') as credentials:
                cred = yaml.safe_load(credentials)
        return cred

def read_yaml(file_path):
        
        with open(file_path, 'r') as file:
                router = yaml.safe_load(file)
        return router


with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_messages = {executor.submit(get_pfe_execption, i['hostname']): i['hostname'] for i in read_yaml('routers.yaml')}
        for future in concurrent.futures.as_completed(future_to_messages):
                match = future_to_messages[future]
                try:
                        datapoint = future.result()
                except Exception as exc:
                        print('%r generated an exception: %s' % (match, exc))
                else:
                        print('\n'.join(datapoint))



