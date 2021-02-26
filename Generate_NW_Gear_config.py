#!/usr/bin/python3
from __future__ import absolute_import,division,print_function
from os import system, name
from time import sleep 
import ipaddress,secrets,json,sys,datetime,shutil,fileinput,os,struct,socket,subprocess


def cidr_to_netmask(cidr):
    network, net_bits = cidr.split('/')
    host_bits = 32 - int(net_bits)
    netmask = socket.inet_ntoa(struct.pack('!I', (1 << 32) - (1 << host_bits)))
    return network, netmask

def clear():
     # for windows 
    if name == 'nt':
        _ = system('cls')
    # for mac and linux(here, os.name is 'posix') 
    else: 
        _ = system('clear') 

def yes_or_no(question):
    reply = str(input(question+" (y/n): ")).lower().strip()
    if reply[0] == "y":
        return 1
    elif reply[0] == "n":
        return 0
    else:
        return yes_or_no("Please Enter again (y/n) ")

def snmp_psk_generated():
    snmp = secrets.token_hex(16)
    psk = secrets.token_hex(16)
    return snmp,psk

def keywords_replace(kw,rp,cid,region,clientfullname,networkdevice):
    with open("/mnt/win_share/config_backup/" + clientfullname + "/" + cid +"/" + cid +"_" + region + "_" +  networkdevice) as f:
        newText=f.read().replace(kw,rp)
    with open("/mnt/win_share/config_backup/" + clientfullname + "/" + cid +"/" + cid +"_" + region + "_" +  networkdevice, "w") as f:
        f.write(newText)
    #os.system("unix2dos /mnt/win_share/config_backup/" + clientfullname + "/" + cid +"/"+ cid +"_" + region + "_" + networkdevice )

def create_cl_dir(cid,clientfullname):
    if not os.path.exists("/mnt/win_share/config_backup/" + clientfullname + "/" + cid + "/"):
        os.makedirs("/mnt/win_share/config_backup/" + clientfullname + "/" + cid + "/")
        result = print("Directory", cid,  clientfullname, "created \n")
    else:
        result = print("Directory", cid,  clientfullname, "already exists will use existing directory \n")
    return result
def text_to_dos():
        FNULL = open(os.devnull, "w")
        retcode = subprocess.Popen(["unix2dos", "/mnt/win_share/config_backup/%s/%s/%s_%s_%s" %(clientfullname,cid,cid,region,networkdevice)], stdout=FNULL, stderr=subprocess.STDOUT)
def full_client_name():
    phrase = input("Client full name? ")
    p_replaced = phrase.replace(" ", "_")
    p_replaced = p_replaced.replace(",","")
    return p_replaced
     
def add_host(devicetype,clientfullname,cid,region):
    with open("/etc/ansible/juniper_config_backup", "a") as myfile:
        addhost = cid + region + "-" + "cl" + "-" + devicetype
        myfile.write(addhost + "       full_client_name=" + clientfullname +"\n")

CLI_networks = []
def question_NW_CLI():
    while True:
        if(yes_or_no("Add CLI networks? ")):
            clear()
            CLI_networks.append(input("Provide a network with CIDR notation Ex. 10.210.10.0/24\n"))
        else:
            break
def add_CLI_networks_L3SW(CLI_networks,cid,region,clientfullname,networkdevice):
    for i in CLI_networks:
        with open("/mnt/win_share/config_backup/" + clientfullname + "/" + cid + "/" + cid +"_" + region + "_" +  networkdevice) as f:
            lines = f.readlines()
            findline = "#ADD_CLI\n"
            appendline = "set policy-options prefix-list CLI-NETWORKS-ALL " + i + "\n"
        lines.insert(lines.index(findline) + 1, appendline)
        with open("/mnt/win_share/config_backup/" + clientfullname + "/" + cid + "/" + cid +"_" + region + "_" +  networkdevice, "w") as f:
            for l in lines:
                f.write(l)
def add_CLI_networks_RTR(CLI_networks,cid,region,clientfullname,networkdevice):
    n = 3
    for i in CLI_networks:
        n+=1
        with open("/mnt/win_share/config_backup/" + clientfullname + "/" + cid + "/" + cid +"_" + region + "_" +  networkdevice) as f:
            lines = f.readlines()
            findline = "#ADD_CLI1\n"
            appendline = "set security address-book global address CLI-NETWORKS-" + str(n) +" " + i + "\n"
            findline2 = "#ADD_CLI2\n"
            appendline2 = "set security address-book global address-set CLI-NETWORKS-ALL address CLI-NETWORKS-" + str(n) + "\n"
        lines.insert(lines.index(findline) + 1, appendline)
        lines.insert(lines.index(findline2) + 1, appendline2)
        with open("/mnt/win_share/config_backup/" + clientfullname + "/" + cid + "/" + cid +"_" + region + "_" +  networkdevice, "w") as f:
            for l in lines:
                f.write(l)
def add_monitoring_east(devicetype,clientfullname,cid,region,rp_snmp):
    if nag_add_option.lower() == "y":
        client_device_arg= cid + region + "-" + "cl" + "-" + devicetype
        client_name_arg=clientfullname
        snmp = rp_snmp
        process = subprocess.Popen(["ansible-playbook /etc/ansible/playbook/NAGIOS/launchAPI_nagio_east.yml -e client_name_arg=%s -e client_device_arg=%s -e snmp=%s" %(client_name_arg,client_device_arg,snmp)],shell=True)
        process.wait()
def add_monitoring_west(devicetype,clientfullname,cid,region,rp_snmp):
    if nag_add_option.lower() == "y":
        client_device_arg= cid + region + "-" + "cl" + "-" + devicetype
        client_name_arg=clientfullname
        snmp = rp_snmp
        process = subprocess.Popen(["ansible-playbook /etc/ansible/playbook/NAGIOS/launchAPI_nagio_west.yml -e client_name_arg=%s -e client_device_arg=%s -e snmp=%s" %(client_name_arg,client_device_arg,snmp)],shell=True)
        process.wait()
def replaceAll(file,searchExp,replaceExp):
    for line in fileinput.input(file, inplace=1):
        if searchExp in line:
            line = line.replace(searchExp,replaceExp)
        sys.stdout.write(line)
def fpc_client(clientfullname,cid,region,networkdevice):
    if fpc.lower() == "y":
        replaceAll("/mnt/win_share/config_backup/" + clientfullname + "/" + cid +"/"+ cid +"_" + region + "_" + networkdevice,"@@njdc3oc@@.220","10.10.51.208")
        replaceAll("/mnt/win_share/config_backup/" + clientfullname + "/" + cid +"/"+ cid +"_" + region + "_" + networkdevice,"@@txdc3oc@@.220","10.120.51.208")
        replaceAll("/mnt/win_share/config_backup/" + clientfullname + "/" + cid +"/"+ cid +"_" + region + "_" + networkdevice,"@@sfdc3oc@@.220","10.10.51.208")
        
clear()
eow =input("East or West coast client? e/w \n")
clientfullname = full_client_name()
cid = input("Client id ? \n").lower()
region = input("Location of client? \n").lower()
create_cl_dir(cid,clientfullname)
fpc = input("Public cloud client? y/n\n")
#nag_add_option = input("Add to nagios check_mk monitoring? y/n\n")
if "e" in eow:
    print("""
                   East Coast Chosen

        1. P2P and DIA (Full config L3 switch and router02) 
        2. 2x DIA (Full config L2 switch with router01 and 02)
        3. 1x DIA RTR01 (Full config L2 switch and router01)
        4. 1x DIA RTR02 (Just router 02 for L2 switch no switch)
        5. L3 SW (Just L3 switch no router)
        6. L2 SW (Just L2 switch no router)    
    """)
    
    n = input("Choose config setup between 1 to 6\n")
    if "1" in n:
        clear()
        print("Configuring East 1. P2P and DIA (Full config L3 switch and router02)\n")
        
        #Inputs
        officesupernet = input("Provide office supernet with subnetmask via CIDR notation Ex. 10.214.20.0/22 \n")
        njdc = input("Provide the NJDC network without subnet mask Ex. 10.121.20.0 \n")
        txdc = input("Provide the TXDC network without subnet mask Ex. 10.221.20.0 \n")
        vlan = input("Provide the vlan of the NJDC/TXDC servers Ex.3742 \n")
        nj_buvpn_tunnel = input("Provide the NJ Backup VPN with subnet mask via CIDR notation Ex.192.168.105.10/30 \n")
        tx_buvpn_tunnel = input("Provide the TX Backup VPN with subnet mask via CIDR notation Ex.192.168.212.10/30 \n")
        #Ask CLI networks
        question_NW_CLI()
        p2p = input("Provide the P2P network with subnetmask via CIDR notation ex. 192.168.105.230/30 \n")
        budia = input("Provide the Backup DIA with subnet mask via CIDR notation Ex.68.20.20.20/29 \n")
        bugw = input("Provide the Backup DIA Gateway without subnet mask \n")
        #OfficeSupernet
        oscidr = officesupernet[-3:]
        subnetmask = cidr_to_netmask(officesupernet)[1]
        fourofficesupernet=officesupernet[:-3]
        threeofficesupernet = officesupernet[:-5]
         
        #Workstation
        officeworkstation = ipaddress.ip_address(fourofficesupernet) + 257
        workstation = str(officeworkstation)
        workstation = workstation[:-1] + "0"
        threenetworkstation = workstation[:-2]

        #Voice
        officevoice = ipaddress.ip_address(fourofficesupernet) + 513
        voice = str(officevoice)
        voice = voice[:-1] + "0"
        threenetvoice = voice[:-2]

        #Isolated
        officeisolated = ipaddress.ip_address(fourofficesupernet) + 771
        isolated = str(officeisolated)
        isolated = isolated[:-1] + "0"
        threenetisolated = isolated[:-2]

        #Backup_DIA
        budia_mask = budia
        budia_wan = budia[:-3]
        
        #NJDC and TXDC
        njdc3oc = njdc[:-2]
        txdc3oc = txdc[:-2]

        #GRE Tunnels NJ and TX Backup
        njbuvpn_tunnel_no_cidr = nj_buvpn_tunnel[:-3]
        njbuvpn_tunnel_only_cidr = nj_buvpn_tunnel[-3:]
        txbuvpn_tunnel_no_cidr = tx_buvpn_tunnel[:-3]
        txbuvpn_tunnel_only_cidr =tx_buvpn_tunnel[-3:]

        njbuvpn_tunn_incr_two = ipaddress.ip_address(str(njbuvpn_tunnel_no_cidr)) + 2
        njbuvpn_tunn_incr_two_cidr = str(njbuvpn_tunn_incr_two) + str(njbuvpn_tunnel_only_cidr)
        
        txbuvpn_tunn_incr_two = ipaddress.ip_address(str(txbuvpn_tunnel_no_cidr)) + 2
        txbuvpn_tunn_incr_two_cidr = str(txbuvpn_tunn_incr_two) + str(txbuvpn_tunnel_only_cidr)
        
                
        njbuvpn_tunn_incr_one = ipaddress.ip_address(str(njbuvpn_tunnel_no_cidr)) + 1
        txbuvpn_tunn_incr_one = ipaddress.ip_address(str(txbuvpn_tunnel_no_cidr)) + 1

        #P2P
        p2p_no_cidr = p2p[:-3]
        p2p_only_cidr = p2p[-3:]
        p2p_increment_one = ipaddress.ip_address(str(p2p_no_cidr)) + 1
        p2p_increment_two = ipaddress.ip_address(str(p2p_no_cidr)) + 2
        p2p_increment_two_with_cidr = str(p2p_increment_two) + str(p2p_only_cidr)
        
        
        #Keywords and replacement
        kw_cid = "@@cid@@"
        rp_cid = cid
        kw_region = "@@region@@"
        rp_region = region
        kw_snmp = "@@snmp@@"
        rp_snmp = snmp_psk_generated()[0]
        kw_psk = "@@psk@@"
        rp_psk = snmp_psk_generated()[1]
        kw_offsunetthree = "@@3osnet@@"
        rp_offsunetthree = threeofficesupernet    
        kw_oscidr = "@@oscidr@@"
        rp_oscidr = oscidr
        kw_budia = "@@budia@@"
        rp_budia = budia_wan 
        kw_budia_mask = "@@budia_mask@@"
        rp_budia_mask = budia_mask
        kw_budiagw = "@@budiagw@@"
        rp_budiagw = bugw
        kw_vlan ="@@vlan@@"
        rp_vlan = vlan
        kw_njbuvpn = "@@njbuvpn@@"
        rp_njbuvpn = njbuvpn_tunnel_no_cidr
        kw_txbuvpn = "@@txbuvpn@@"  
        rp_txbuvpn = txbuvpn_tunnel_no_cidr
        kw_njbuvpn_cidr = "@@njbuvpn_cidr@@"
        rp_njbuvpn_cidr =nj_buvpn_tunnel
        kw_txbuvpn_cidr = "@@txbuvpn_cidr@@"
        rp_txbuvpn_cidr =tx_buvpn_tunnel
        kw_njbuvpn_1= "@@backup_nj_tunnel1incr@@"
        rp_njbuvpn_1=str(njbuvpn_tunn_incr_one)
        kw_txbuvpn_1="@@backup_tx_tunnel1incr@@"
        rp_txbuvpn_1=str(txbuvpn_tunn_incr_one)
        kw_njbuvpn_2= "@@njbuvpn2@@"
        rp_njbuvpn_2=njbuvpn_tunn_incr_two_cidr
        kw_txbuvpn_2="@@txbuvpn2@@"
        rp_txbuvpn_2=txbuvpn_tunn_incr_two_cidr
        kw_osunet_subnetmask="@@subnetmask@@"
        rp_osunet_subnetmask=subnetmask
        kw_p2p = "@@p2pog@@"
        rp_p2p =p2p_no_cidr
        kw_p2p_cidr= "@@p2pog_cidr@@"
        rp_p2p_cidr=p2p
        kw_p2pincr1 = "@@p2pdcside@@"
        rp_p2pincr1 = str(p2p_increment_one)
        kw_p2pincr2 ="@@p2pclientside@@"
        rp_p2pincr2 =str(p2p_increment_two_with_cidr)
        kw_njdc3oc = "@@njdc3oc@@"
        rp_njdc3oc = njdc3oc
        kw_txdc3oc = "@@txdc3oc@@"
        rp_txdc3oc = txdc3oc
        kw_three_workstation = "@@3osnetworkstation@@"
        rp_three_workstation =threenetworkstation
        kw_three_voice = "@@3osvoice@@"
        rp_three_voice =threenetvoice
        kw_three_isolated = "@@3isolatednet@@"
        rp_three_isolated =threenetisolated
        
        #Juniper router02
        
        networkdevice ="E_p2p_dia_rtr02.txt"
        shutil.copy("/mnt/win_share/builds/config_files/East/1_P2P_and_DIA/" + networkdevice,"/mnt/win_share/config_backup/" + clientfullname + "/" + cid +"/"+ cid +"_" + region + "_" + networkdevice)
        #Replace
        keywords_replace(kw_cid,rp_cid,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_region,rp_region,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_snmp,rp_snmp,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_psk,rp_psk,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_offsunetthree,rp_offsunetthree,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_oscidr,rp_oscidr,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_vlan,rp_vlan,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_budia,rp_budia,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_budia_mask,rp_budia_mask,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_budiagw,rp_budiagw,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njbuvpn_2,rp_njbuvpn_2,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txbuvpn_2,rp_txbuvpn_2,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njbuvpn,rp_njbuvpn,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txbuvpn,rp_txbuvpn,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njdc3oc,rp_njdc3oc,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txdc3oc,rp_txdc3oc,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njbuvpn_cidr,rp_njbuvpn_cidr,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txbuvpn_cidr,rp_txbuvpn_cidr,cid,region,clientfullname,networkdevice)
        devicetype = "rtr02"
        add_host(devicetype,clientfullname,cid,region)
        add_CLI_networks_RTR(CLI_networks,cid,region,clientfullname,networkdevice)
        text_to_dos()
        #add_monitoring_east(devicetype,clientfullname,cid,region,rp_snmp)
        #Juniper switch01 24P and 48P
        
        networkdevice ="E_p2p_dia_sw01_24P.txt"
        shutil.copy("/mnt/win_share/builds/config_files/East/1_P2P_and_DIA/" + networkdevice,"/mnt/win_share/config_backup/" + clientfullname + "/" + cid +"/"+ cid +"_" + region + "_" + networkdevice)
        #Replace
        fpc_client(clientfullname,cid,region,networkdevice)
        keywords_replace(kw_cid,rp_cid,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_region,rp_region,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_snmp,rp_snmp,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_psk,rp_psk,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_offsunetthree,rp_offsunetthree,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_oscidr,rp_oscidr,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_vlan,rp_vlan,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_budia,rp_budia,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_budia_mask,rp_budia_mask,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_budiagw,rp_budiagw,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njdc3oc,rp_njdc3oc,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txdc3oc,rp_txdc3oc,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_p2pincr2,rp_p2pincr2,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_p2p,rp_p2p,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_workstation,rp_three_workstation,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_voice,rp_three_voice,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_isolated,rp_three_isolated,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_p2p_cidr,rp_p2p_cidr,cid,region,clientfullname,networkdevice)
        add_CLI_networks_L3SW(CLI_networks,cid,region,clientfullname,networkdevice)
        text_to_dos()
        #48P
        networkdevice ="E_p2p_dia_sw01_48P.txt"
        shutil.copy("/mnt/win_share/builds/config_files/East/1_P2P_and_DIA/" + networkdevice,"/mnt/win_share/config_backup/" + clientfullname + "/" + cid +"/"+ cid +"_" + region + "_" + networkdevice)
        #Replace
        fpc_client(clientfullname,cid,region,networkdevice)
        keywords_replace(kw_cid,rp_cid,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_region,rp_region,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_snmp,rp_snmp,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_psk,rp_psk,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_offsunetthree,rp_offsunetthree,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_oscidr,rp_oscidr,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_vlan,rp_vlan,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_budia,rp_budia,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_budia_mask,rp_budia_mask,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_budiagw,rp_budiagw,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njdc3oc,rp_njdc3oc,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txdc3oc,rp_txdc3oc,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_p2pincr2,rp_p2pincr2,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_p2p,rp_p2p,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_workstation,rp_three_workstation,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_voice,rp_three_voice,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_isolated,rp_three_isolated,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_p2p_cidr,rp_p2p_cidr,cid,region,clientfullname,networkdevice)
        devicetype = "sw01"
        add_host(devicetype,clientfullname,cid,region)
        add_CLI_networks_L3SW(CLI_networks,cid,region,clientfullname,networkdevice)
        text_to_dos()
        #add_monitoring_east(devicetype,clientfullname,cid,region,rp_snmp)
        #GRE Tunnels
        
        networkdevice = "E_p2p_dia_gre_tnl_rtrvpn02.txt"
        shutil.copy("/mnt/win_share/builds/config_files/East/1_P2P_and_DIA/" + networkdevice,"/mnt/win_share/config_backup/" + clientfullname + "/" + cid +"/"+ cid +"_" + region + "_" + networkdevice)
        #Replace
        keywords_replace(kw_vlan,rp_vlan,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_cid,rp_cid,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_oscidr,rp_oscidr,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_offsunetthree,rp_offsunetthree,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_region,rp_region,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_budia,rp_budia,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_psk,rp_psk,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njbuvpn,rp_njbuvpn,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txbuvpn,rp_txbuvpn,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njbuvpn_1,rp_njbuvpn_1,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txbuvpn_1,rp_txbuvpn_1,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_osunet_subnetmask,rp_osunet_subnetmask,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_p2p,rp_p2p,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_p2pincr1,rp_p2pincr1,cid,region,clientfullname,networkdevice)
        text_to_dos()
    elif "2" in n:
        clear()
        print("Configuring East 2. 2x DIA (Full config L2 switch with router01 and 02)")

        #Inputs
        officesupernet = input("Provide office supernet with subnetmask via CIDR notation Ex. 10.214.20.0/22 \n")
        njdc = input("Provide the NJDC network without subnet mask Ex. 10.121.20.0 \n")
        txdc = input("Provide the TXDC network without subnet mask Ex. 10.221.20.0 \n")
        vlan = input("Provide the vlan of the NJDC/TXDC servers Ex.3742 \n")
        nj_prvpn_tunnel = input("Provide the NJ Primary VPN with subnet mask via CIDR notation Ex.192.168.105.10/30 \n")
        tx_prvpn_tunnel = input("Provide the TX Primary VPN with subnet mask via CIDR notation Ex.192.168.212.10/30 \n")        
        nj_buvpn_tunnel = input("Provide the NJ Backup  VPN with subnet mask via CIDR notation Ex.192.168.105.10/30 \n")
        tx_buvpn_tunnel = input("Provide the TX Backup  VPN with subnet mask via CIDR notation Ex.192.168.212.10/30 \n")
        #Ask CLI networks
        question_NW_CLI()
        prdia = input("Provide the Primary DIA with subnet mask via CIDR notation Ex.68.20.20.20/29 \n")
        prgw = input("Provide the Primary DIA Gateway without subnet mask \n")
        budia = input("Provide the Backup  DIA with subnet mask via CIDR notation Ex.68.20.20.20/29 \n")
        bugw = input("Provide the Backup  DIA Gateway without subnet mask \n")


        #OfficeSupernet
        oscidr = officesupernet[-3:]
        subnetmask = cidr_to_netmask(officesupernet)[1]
        fourofficesupernet=officesupernet[:-3]
        threeofficesupernet = officesupernet[:-5]
         
        #Workstation
        officeworkstation = ipaddress.ip_address(fourofficesupernet) + 257
        workstation = str(officeworkstation)
        workstation = workstation[:-1] + "0"
        threenetworkstation = workstation[:-2]

        #Voice
        officevoice = ipaddress.ip_address(fourofficesupernet) + 513
        voice = str(officevoice)
        voice = voice[:-1] + "0"
        threenetvoice = voice[:-2]

        #Isolated
        officeisolated = ipaddress.ip_address(fourofficesupernet) + 771
        isolated = str(officeisolated)
        isolated = isolated[:-1] + "0"
        threenetisolated = isolated[:-2]

        #Primary DIA
        prdia_mask = prdia
        prdia_wan = prdia[:-3]

        #Backup_DIA
        budia_mask = budia
        budia_wan = budia[:-3]
        
        #NJDC and TXDC
        njdc3oc = njdc[:-2]
        txdc3oc = txdc[:-2]


        #GRE Tunnels NJ and TX Primary
        njprvpn_tunnel_no_cidr = nj_prvpn_tunnel[:-3]
        njprvpn_tunnel_only_cidr = nj_prvpn_tunnel[-3:]
        txprvpn_tunnel_no_cidr = tx_prvpn_tunnel[:-3]
        txprvpn_tunnel_only_cidr =tx_prvpn_tunnel[-3:]

        njprvpn_tunn_incr_two = ipaddress.ip_address(str(njprvpn_tunnel_no_cidr)) + 2
        njprvpn_tunn_incr_two_cidr = str(njprvpn_tunn_incr_two) + str(njprvpn_tunnel_only_cidr)
        
        txprvpn_tunn_incr_two = ipaddress.ip_address(str(txprvpn_tunnel_no_cidr)) + 2
        txprvpn_tunn_incr_two_cidr = str(txprvpn_tunn_incr_two) + str(txprvpn_tunnel_only_cidr)
        
                
        njprvpn_tunn_incr_one = ipaddress.ip_address(str(njprvpn_tunnel_no_cidr)) + 1
        txprvpn_tunn_incr_one = ipaddress.ip_address(str(txprvpn_tunnel_no_cidr)) + 1

        #GRE Tunnels NJ and TX Backup
        njbuvpn_tunnel_no_cidr = nj_buvpn_tunnel[:-3]
        njbuvpn_tunnel_only_cidr = nj_buvpn_tunnel[-3:]
        txbuvpn_tunnel_no_cidr = tx_buvpn_tunnel[:-3]
        txbuvpn_tunnel_only_cidr =tx_buvpn_tunnel[-3:]

        njbuvpn_tunn_incr_two = ipaddress.ip_address(str(njbuvpn_tunnel_no_cidr)) + 2
        njbuvpn_tunn_incr_two_cidr = str(njbuvpn_tunn_incr_two) + str(njbuvpn_tunnel_only_cidr)
        
        txbuvpn_tunn_incr_two = ipaddress.ip_address(str(txbuvpn_tunnel_no_cidr)) + 2
        txbuvpn_tunn_incr_two_cidr = str(txbuvpn_tunn_incr_two) + str(txbuvpn_tunnel_only_cidr)
        
                
        njbuvpn_tunn_incr_one = ipaddress.ip_address(str(njbuvpn_tunnel_no_cidr)) + 1
        txbuvpn_tunn_incr_one = ipaddress.ip_address(str(txbuvpn_tunnel_no_cidr)) + 1

        #Keywords and replacement
        kw_cid = "@@cid@@"
        rp_cid = cid
        kw_region = "@@region@@"
        rp_region = region
        kw_snmp = "@@snmp@@"
        rp_snmp = snmp_psk_generated()[0]
        kw_psk = "@@psk@@"
        rp_psk = snmp_psk_generated()[1]
        kw_offsunetthree = "@@3osnet@@"
        rp_offsunetthree = threeofficesupernet    
        kw_oscidr = "@@oscidr@@"
        rp_oscidr = oscidr
        #Primary DIA
        kw_prdia = "@@prdia@@"
        rp_prdia = prdia_wan 
        kw_prdia_mask = "@@prdia_mask@@"
        rp_prdia_mask = prdia_mask
        kw_prdiagw = "@@prdiagw@@"
        rp_prdiagw = prgw
        #Backup DIA
        kw_budia = "@@budia@@"
        rp_budia = budia_wan 
        kw_budia_mask = "@@budia_mask@@"
        rp_budia_mask = budia_mask
        kw_budiagw = "@@budiagw@@"
        rp_budiagw = bugw
        #Vlan
        kw_vlan ="@@vlan@@"
        rp_vlan = vlan
        #Primary
        kw_njprvpn = "@@njprvpn@@"
        rp_njprvpn = njprvpn_tunnel_no_cidr
        kw_txprvpn = "@@txprvpn@@"  
        rp_txprvpn = txprvpn_tunnel_no_cidr
        kw_njprvpn_cidr = "@@njprvpn_cidr@@"
        rp_njprvpn_cidr =nj_prvpn_tunnel
        kw_txprvpn_cidr = "@@txprvpn_cidr@@"
        rp_txprvpn_cidr =tx_prvpn_tunnel
        kw_njprvpn_1= "@@primary_nj_tunnel1incr@@"
        rp_njprvpn_1=str(njprvpn_tunn_incr_one)
        kw_txprvpn_1="@@primary_tx_tunnel1incr@@"
        rp_txprvpn_1=str(txprvpn_tunn_incr_one)
        kw_njprvpn_2= "@@njprvpn2@@"
        rp_njprvpn_2=njprvpn_tunn_incr_two_cidr
        kw_txprvpn_2="@@txprvpn2@@"
        rp_txprvpn_2=txprvpn_tunn_incr_two_cidr
        #Backup
        kw_njbuvpn = "@@njbuvpn@@"
        rp_njbuvpn = njbuvpn_tunnel_no_cidr
        kw_txbuvpn = "@@txbuvpn@@"  
        rp_txbuvpn = txbuvpn_tunnel_no_cidr
        kw_njbuvpn_cidr = "@@njbuvpn_cidr@@"
        rp_njbuvpn_cidr =nj_buvpn_tunnel
        kw_txbuvpn_cidr = "@@txbuvpn_cidr@@"
        rp_txbuvpn_cidr =tx_buvpn_tunnel
        kw_njbuvpn_1= "@@backup_nj_tunnel1incr@@"
        rp_njbuvpn_1=str(njbuvpn_tunn_incr_one)
        kw_txbuvpn_1="@@backup_tx_tunnel1incr@@"
        rp_txbuvpn_1=str(txbuvpn_tunn_incr_one)
        kw_njbuvpn_2= "@@njbuvpn2@@"
        rp_njbuvpn_2=njbuvpn_tunn_incr_two_cidr
        kw_txbuvpn_2="@@txbuvpn2@@"
        rp_txbuvpn_2=txbuvpn_tunn_incr_two_cidr
        #Office supernet subnetmask
        kw_osunet_subnetmask="@@subnetmask@@"
        rp_osunet_subnetmask=subnetmask
        #DCs
        kw_njdc3oc = "@@njdc3oc@@"
        rp_njdc3oc = njdc3oc
        kw_txdc3oc = "@@txdc3oc@@"
        rp_txdc3oc = txdc3oc
        kw_three_workstation = "@@3osnetworkstation@@"
        rp_three_workstation =threenetworkstation
        kw_three_voice = "@@3osvoice@@"
        rp_three_voice =threenetvoice
        kw_three_isolated = "@@3isolatednet@@"
        rp_three_isolated =threenetisolated

        #Juniper router01
        
        networkdevice ="E_2x_dia_rtr01.txt"
        shutil.copy("/mnt/win_share/builds/config_files/East/2_2x_DIA/" + networkdevice,"/mnt/win_share/config_backup/" + clientfullname + "/" + cid +"/"+ cid +"_" + region + "_" + networkdevice)
        #Replace
        fpc_client(clientfullname,cid,region,networkdevice)
        keywords_replace(kw_cid,rp_cid,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_region,rp_region,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_snmp,rp_snmp,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_psk,rp_psk,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_offsunetthree,rp_offsunetthree,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_oscidr,rp_oscidr,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_vlan,rp_vlan,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_prdia,rp_prdia,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_prdia_mask,rp_prdia_mask,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_prdiagw,rp_prdiagw,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njprvpn_2,rp_njprvpn_2,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txprvpn_2,rp_txprvpn_2,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njprvpn,rp_njprvpn,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txprvpn,rp_txprvpn,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njdc3oc,rp_njdc3oc,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txdc3oc,rp_txdc3oc,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njprvpn_cidr,rp_njprvpn_cidr,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txprvpn_cidr,rp_txprvpn_cidr,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_workstation,rp_three_workstation,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_voice,rp_three_voice,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_isolated,rp_three_isolated,cid,region,clientfullname,networkdevice)
        devicetype = "rtr01"
        add_host(devicetype,clientfullname,cid,region)
        add_CLI_networks_RTR(CLI_networks,cid,region,clientfullname,networkdevice)
        text_to_dos()
        #add_monitoring_east(devicetype,clientfullname,cid,region,rp_snmp)
        #Juniper router02
        
        networkdevice ="E_2x_dia_rtr02.txt"
        shutil.copy("/mnt/win_share/builds/config_files/East/2_2x_DIA/" + networkdevice,"/mnt/win_share/config_backup/" + clientfullname + "/" + cid +"/"+ cid +"_" + region + "_" + networkdevice)
        #Replace
        fpc_client(clientfullname,cid,region,networkdevice)
        keywords_replace(kw_cid,rp_cid,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_region,rp_region,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_snmp,rp_snmp,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_psk,rp_psk,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_offsunetthree,rp_offsunetthree,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_oscidr,rp_oscidr,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_vlan,rp_vlan,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_budia,rp_budia,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_budia_mask,rp_budia_mask,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_budiagw,rp_budiagw,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njbuvpn_2,rp_njbuvpn_2,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txbuvpn_2,rp_txbuvpn_2,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njbuvpn,rp_njbuvpn,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txbuvpn,rp_txbuvpn,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njdc3oc,rp_njdc3oc,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txdc3oc,rp_txdc3oc,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njbuvpn_cidr,rp_njbuvpn_cidr,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txbuvpn_cidr,rp_txbuvpn_cidr,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_workstation,rp_three_workstation,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_voice,rp_three_voice,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_isolated,rp_three_isolated,cid,region,clientfullname,networkdevice)
        devicetype = "rtr02"
        add_host(devicetype,clientfullname,cid,region)
        add_CLI_networks_RTR(CLI_networks,cid,region,clientfullname,networkdevice)
        text_to_dos()
        #add_monitoring_east(devicetype,clientfullname,cid,region,rp_snmp)
        #Juniper switch01 24P and 48P
        
        networkdevice ="E_2x_dia_sw01_24P.txt"
        shutil.copy("/mnt/win_share/builds/config_files/East/2_2x_DIA/" + networkdevice,"/mnt/win_share/config_backup/" + clientfullname + "/" + cid +"/"+ cid +"_" + region + "_" + networkdevice)
        #Replace
        keywords_replace(kw_cid,rp_cid,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_region,rp_region,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_snmp,rp_snmp,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_psk,rp_psk,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_offsunetthree,rp_offsunetthree,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_oscidr,rp_oscidr,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njdc3oc,rp_njdc3oc,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txdc3oc,rp_txdc3oc,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_workstation,rp_three_workstation,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_voice,rp_three_voice,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_isolated,rp_three_isolated,cid,region,clientfullname,networkdevice)
        text_to_dos()
        
        networkdevice ="E_2x_dia_sw01_48P.txt"
        shutil.copy("/mnt/win_share/builds/config_files/East/2_2x_DIA/" + networkdevice,"/mnt/win_share/config_backup/" + clientfullname + "/" + cid +"/"+ cid +"_" + region + "_" + networkdevice)
        #Replace
        keywords_replace(kw_cid,rp_cid,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_region,rp_region,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_snmp,rp_snmp,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_psk,rp_psk,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_offsunetthree,rp_offsunetthree,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_oscidr,rp_oscidr,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njdc3oc,rp_njdc3oc,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txdc3oc,rp_txdc3oc,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_workstation,rp_three_workstation,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_voice,rp_three_voice,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_isolated,rp_three_isolated,cid,region,clientfullname,networkdevice)
        devicetype = "sw01"
        add_host(devicetype,clientfullname,cid,region)
        text_to_dos()
        #add_monitoring_east(devicetype,clientfullname,cid,region,rp_snmp)
        
        #GRE Tunnels Primary and Backup


        networkdevice = "E_dia_gre_tnl_rtrvpn01.txt"
        shutil.copy("/mnt/win_share/builds/config_files/East/2_2x_DIA/" + networkdevice,"/mnt/win_share/config_backup/" + clientfullname + "/" + cid +"/"+ cid +"_" + region + "_" + networkdevice)
        #Replace
        keywords_replace(kw_vlan,rp_vlan,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_cid,rp_cid,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_oscidr,rp_oscidr,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_offsunetthree,rp_offsunetthree,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_region,rp_region,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_prdia,rp_prdia,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_psk,rp_psk,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njprvpn,rp_njprvpn,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txprvpn,rp_txprvpn,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njprvpn_1,rp_njprvpn_1,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txprvpn_1,rp_txprvpn_1,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_osunet_subnetmask,rp_osunet_subnetmask,cid,region,clientfullname,networkdevice)
        text_to_dos()
        
        networkdevice = "E_dia_gre_tnl_rtrvpn02.txt"
        shutil.copy("/mnt/win_share/builds/config_files/East/2_2x_DIA/" + networkdevice,"/mnt/win_share/config_backup/" + clientfullname + "/" + cid +"/"+ cid +"_" + region + "_" + networkdevice)
        #Replace
        keywords_replace(kw_vlan,rp_vlan,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_cid,rp_cid,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_oscidr,rp_oscidr,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_offsunetthree,rp_offsunetthree,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_region,rp_region,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_budia,rp_budia,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_psk,rp_psk,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njbuvpn,rp_njbuvpn,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txbuvpn,rp_txbuvpn,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njbuvpn_1,rp_njbuvpn_1,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txbuvpn_1,rp_txbuvpn_1,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_osunet_subnetmask,rp_osunet_subnetmask,cid,region,clientfullname,networkdevice)
        text_to_dos()


    elif "3" in n:
        clear()
        print("Configuring East 3. 1x DIA RTR01 (Full config L2 switch and router01)")

        #Inputs
        officesupernet = input("Provide office supernet with subnetmask via CIDR notation Ex. 10.214.20.0/22 \n")
        njdc = input("Provide the NJDC network without subnet mask Ex. 10.121.20.0 \n")
        txdc = input("Provide the TXDC network without subnet mask Ex. 10.221.20.0 \n")
        vlan = input("Provide the vlan of the NJDC/TXDC servers Ex.3742 \n")
        nj_prvpn_tunnel = input("Provide the NJ Primary VPN with subnet mask via CIDR notation Ex.192.168.105.10/30 \n")
        tx_prvpn_tunnel = input("Provide the TX Primary VPN with subnet mask via CIDR notation Ex.192.168.212.10/30 \n")        
        #Ask CLI networks
        question_NW_CLI()
        prdia = input("Provide the Primary DIA with subnet mask via CIDR notation Ex.68.20.20.20/29 \n")
        prgw = input("Provide the Primary DIA Gateway without subnet mask \n")

        #OfficeSupernet
        oscidr = officesupernet[-3:]
        subnetmask = cidr_to_netmask(officesupernet)[1]
        fourofficesupernet=officesupernet[:-3]
        threeofficesupernet = officesupernet[:-5]
         
        #Workstation
        officeworkstation = ipaddress.ip_address(fourofficesupernet) + 257
        workstation = str(officeworkstation)
        workstation = workstation[:-1] + "0"
        threenetworkstation = workstation[:-2]

        #Voice
        officevoice = ipaddress.ip_address(fourofficesupernet) + 513
        voice = str(officevoice)
        voice = voice[:-1] + "0"
        threenetvoice = voice[:-2]

        #Isolated
        officeisolated = ipaddress.ip_address(fourofficesupernet) + 771
        isolated = str(officeisolated)
        isolated = isolated[:-1] + "0"
        threenetisolated = isolated[:-2]

        #Primary DIA
        prdia_mask = prdia
        prdia_wan = prdia[:-3]

        
        #NJDC and TXDC
        njdc3oc = njdc[:-2]
        txdc3oc = txdc[:-2]


        #GRE Tunnels NJ and TX Primary
        njprvpn_tunnel_no_cidr = nj_prvpn_tunnel[:-3]
        njprvpn_tunnel_only_cidr = nj_prvpn_tunnel[-3:]
        txprvpn_tunnel_no_cidr = tx_prvpn_tunnel[:-3]
        txprvpn_tunnel_only_cidr =tx_prvpn_tunnel[-3:]

        njprvpn_tunn_incr_two = ipaddress.ip_address(str(njprvpn_tunnel_no_cidr)) + 2
        njprvpn_tunn_incr_two_cidr = str(njprvpn_tunn_incr_two) + str(njprvpn_tunnel_only_cidr)
        
        txprvpn_tunn_incr_two = ipaddress.ip_address(str(txprvpn_tunnel_no_cidr)) + 2
        txprvpn_tunn_incr_two_cidr = str(txprvpn_tunn_incr_two) + str(txprvpn_tunnel_only_cidr)
        
                
        njprvpn_tunn_incr_one = ipaddress.ip_address(str(njprvpn_tunnel_no_cidr)) + 1
        txprvpn_tunn_incr_one = ipaddress.ip_address(str(txprvpn_tunnel_no_cidr)) + 1


        #Keywords and replacement
        kw_cid = "@@cid@@"
        rp_cid = cid
        kw_region = "@@region@@"
        rp_region = region
        kw_snmp = "@@snmp@@"
        rp_snmp = snmp_psk_generated()[0]
        kw_psk = "@@psk@@"
        rp_psk = snmp_psk_generated()[1]
        kw_offsunetthree = "@@3osnet@@"
        rp_offsunetthree = threeofficesupernet    
        kw_oscidr = "@@oscidr@@"
        rp_oscidr = oscidr
        #Primary DIA
        kw_prdia = "@@prdia@@"
        rp_prdia = prdia_wan 
        kw_prdia_mask = "@@prdia_mask@@"
        rp_prdia_mask = prdia_mask
        kw_prdiagw = "@@prdiagw@@"
        rp_prdiagw = prgw
        #Vlan
        kw_vlan ="@@vlan@@"
        rp_vlan = vlan
        #Primary
        kw_njprvpn = "@@njprvpn@@"
        rp_njprvpn = njprvpn_tunnel_no_cidr
        kw_txprvpn = "@@txprvpn@@"  
        rp_txprvpn = txprvpn_tunnel_no_cidr
        kw_njprvpn_cidr = "@@njprvpn_cidr@@"
        rp_njprvpn_cidr =nj_prvpn_tunnel
        kw_txprvpn_cidr = "@@txprvpn_cidr@@"
        rp_txprvpn_cidr =tx_prvpn_tunnel
        kw_njprvpn_1= "@@primary_nj_tunnel1incr@@"
        rp_njprvpn_1=str(njprvpn_tunn_incr_one)
        kw_txprvpn_1="@@primary_tx_tunnel1incr@@"
        rp_txprvpn_1=str(txprvpn_tunn_incr_one)
        kw_njprvpn_2= "@@njprvpn2@@"
        rp_njprvpn_2=njprvpn_tunn_incr_two_cidr
        kw_txprvpn_2="@@txprvpn2@@"
        rp_txprvpn_2=txprvpn_tunn_incr_two_cidr
        #Office supernet subnetmask
        kw_osunet_subnetmask="@@subnetmask@@"
        rp_osunet_subnetmask=subnetmask
        #DCs
        kw_njdc3oc = "@@njdc3oc@@"
        rp_njdc3oc = njdc3oc
        kw_txdc3oc = "@@txdc3oc@@"
        rp_txdc3oc = txdc3oc
        kw_three_workstation = "@@3osnetworkstation@@"
        rp_three_workstation =threenetworkstation
        kw_three_voice = "@@3osvoice@@"
        rp_three_voice =threenetvoice
        kw_three_isolated = "@@3isolatednet@@"
        rp_three_isolated =threenetisolated

        #Juniper router01
        
        networkdevice ="E_2x_dia_rtr01.txt"
        shutil.copy("/mnt/win_share/builds/config_files/East/2_2x_DIA/" + networkdevice,"/mnt/win_share/config_backup/" + clientfullname + "/" + cid +"/"+ cid +"_" + region + "_" + networkdevice)
        #Replace
        fpc_client(clientfullname,cid,region,networkdevice)
        keywords_replace(kw_cid,rp_cid,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_region,rp_region,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_snmp,rp_snmp,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_psk,rp_psk,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_offsunetthree,rp_offsunetthree,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_oscidr,rp_oscidr,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_vlan,rp_vlan,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_prdia,rp_prdia,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_prdia_mask,rp_prdia_mask,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_prdiagw,rp_prdiagw,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njprvpn_2,rp_njprvpn_2,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txprvpn_2,rp_txprvpn_2,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njprvpn,rp_njprvpn,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txprvpn,rp_txprvpn,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njdc3oc,rp_njdc3oc,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txdc3oc,rp_txdc3oc,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njprvpn_cidr,rp_njprvpn_cidr,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txprvpn_cidr,rp_txprvpn_cidr,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_workstation,rp_three_workstation,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_voice,rp_three_voice,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_isolated,rp_three_isolated,cid,region,clientfullname,networkdevice)
        devicetype = "rtr01"
        add_host(devicetype,clientfullname,cid,region)
        add_CLI_networks_RTR(CLI_networks,cid,region,clientfullname,networkdevice)
        text_to_dos()
        #add_monitoring_east(devicetype,clientfullname,cid,region,rp_snmp)
        #Juniper switch01 24P and 48P
        
        networkdevice ="E_2x_dia_sw01_24P.txt"
        shutil.copy("/mnt/win_share/builds/config_files/East/2_2x_DIA/" + networkdevice,"/mnt/win_share/config_backup/" + clientfullname + "/" + cid +"/"+ cid +"_" + region + "_" + networkdevice)
        #Replace
        keywords_replace(kw_cid,rp_cid,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_region,rp_region,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_snmp,rp_snmp,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_psk,rp_psk,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_offsunetthree,rp_offsunetthree,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_oscidr,rp_oscidr,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njdc3oc,rp_njdc3oc,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txdc3oc,rp_txdc3oc,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_workstation,rp_three_workstation,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_voice,rp_three_voice,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_isolated,rp_three_isolated,cid,region,clientfullname,networkdevice)
        text_to_dos()
        
        networkdevice ="E_2x_dia_sw01_48P.txt"
        shutil.copy("/mnt/win_share/builds/config_files/East/2_2x_DIA/" + networkdevice,"/mnt/win_share/config_backup/" + clientfullname + "/" + cid +"/"+ cid +"_" + region + "_" + networkdevice)
        #Replace
        keywords_replace(kw_cid,rp_cid,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_region,rp_region,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_snmp,rp_snmp,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_psk,rp_psk,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_offsunetthree,rp_offsunetthree,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_oscidr,rp_oscidr,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njdc3oc,rp_njdc3oc,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txdc3oc,rp_txdc3oc,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_workstation,rp_three_workstation,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_voice,rp_three_voice,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_isolated,rp_three_isolated,cid,region,clientfullname,networkdevice)
        devicetype = "sw01"
        add_host(devicetype,clientfullname,cid,region)
        text_to_dos()
        #add_monitoring_east(devicetype,clientfullname,cid,region,rp_snmp)
        
        #GRE Tunnels Primary and Backup


        networkdevice = "E_dia_gre_tnl_rtrvpn01.txt"
        shutil.copy("/mnt/win_share/builds/config_files/East/2_2x_DIA/" + networkdevice,"/mnt/win_share/config_backup/" + clientfullname + "/" + cid +"/"+ cid +"_" + region + "_" + networkdevice)
        #Replace
        keywords_replace(kw_vlan,rp_vlan,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_cid,rp_cid,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_oscidr,rp_oscidr,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_offsunetthree,rp_offsunetthree,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_region,rp_region,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_prdia,rp_prdia,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_psk,rp_psk,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njprvpn,rp_njprvpn,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txprvpn,rp_txprvpn,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njprvpn_1,rp_njprvpn_1,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txprvpn_1,rp_txprvpn_1,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_osunet_subnetmask,rp_osunet_subnetmask,cid,region,clientfullname,networkdevice)
        text_to_dos()

    elif "4" in n:
        clear()
        print("Configuring East 4. 1x DIA RTR02 (Just router 02 for L2 switch no switch)")

        #Inputs
        officesupernet = input("Provide office supernet with subnetmask via CIDR notation Ex. 10.214.20.0/22 \n")
        njdc = input("Provide the NJDC network without subnet mask Ex. 10.121.20.0 \n")
        txdc = input("Provide the TXDC network without subnet mask Ex. 10.221.20.0 \n")
        vlan = input("Provide the vlan of the NJDC/TXDC servers Ex.3742 \n")       
        nj_buvpn_tunnel = input("Provide the NJ Backup  VPN with subnet mask via CIDR notation Ex.192.168.105.10/30 \n")
        tx_buvpn_tunnel = input("Provide the TX Backup  VPN with subnet mask via CIDR notation Ex.192.168.212.10/30 \n")
        #Ask CLI networks
        question_NW_CLI()
        budia = input("Provide the Backup  DIA with subnet mask via CIDR notation Ex.68.20.20.20/29 \n")
        bugw = input("Provide the Backup  DIA Gateway without subnet mask \n")

        #OfficeSupernet
        oscidr = officesupernet[-3:]
        subnetmask = cidr_to_netmask(officesupernet)[1]
        fourofficesupernet=officesupernet[:-3]
        threeofficesupernet = officesupernet[:-5]
         
        #Workstation
        officeworkstation = ipaddress.ip_address(fourofficesupernet) + 257
        workstation = str(officeworkstation)
        workstation = workstation[:-1] + "0"
        threenetworkstation = workstation[:-2]

        #Voice
        officevoice = ipaddress.ip_address(fourofficesupernet) + 513
        voice = str(officevoice)
        voice = voice[:-1] + "0"
        threenetvoice = voice[:-2]

        #Isolated
        officeisolated = ipaddress.ip_address(fourofficesupernet) + 771
        isolated = str(officeisolated)
        isolated = isolated[:-1] + "0"
        threenetisolated = isolated[:-2]


        #Backup_DIA
        budia_mask = budia
        budia_wan = budia[:-3]
        
        #NJDC and TXDC
        njdc3oc = njdc[:-2]
        txdc3oc = txdc[:-2]



        #GRE Tunnels NJ and TX Backup
        njbuvpn_tunnel_no_cidr = nj_buvpn_tunnel[:-3]
        njbuvpn_tunnel_only_cidr = nj_buvpn_tunnel[-3:]
        txbuvpn_tunnel_no_cidr = tx_buvpn_tunnel[:-3]
        txbuvpn_tunnel_only_cidr =tx_buvpn_tunnel[-3:]

        njbuvpn_tunn_incr_two = ipaddress.ip_address(str(njbuvpn_tunnel_no_cidr)) + 2
        njbuvpn_tunn_incr_two_cidr = str(njbuvpn_tunn_incr_two) + str(njbuvpn_tunnel_only_cidr)
        
        txbuvpn_tunn_incr_two = ipaddress.ip_address(str(txbuvpn_tunnel_no_cidr)) + 2
        txbuvpn_tunn_incr_two_cidr = str(txbuvpn_tunn_incr_two) + str(txbuvpn_tunnel_only_cidr)
        
                
        njbuvpn_tunn_incr_one = ipaddress.ip_address(str(njbuvpn_tunnel_no_cidr)) + 1
        txbuvpn_tunn_incr_one = ipaddress.ip_address(str(txbuvpn_tunnel_no_cidr)) + 1

        #Keywords and replacement
        kw_cid = "@@cid@@"
        rp_cid = cid
        kw_region = "@@region@@"
        rp_region = region
        kw_snmp = "@@snmp@@"
        rp_snmp = snmp_psk_generated()[0]
        kw_psk = "@@psk@@"
        rp_psk = snmp_psk_generated()[1]
        kw_offsunetthree = "@@3osnet@@"
        rp_offsunetthree = threeofficesupernet    
        kw_oscidr = "@@oscidr@@"
        rp_oscidr = oscidr
        #Backup DIA
        kw_budia = "@@budia@@"
        rp_budia = budia_wan 
        kw_budia_mask = "@@budia_mask@@"
        rp_budia_mask = budia_mask
        kw_budiagw = "@@budiagw@@"
        rp_budiagw = bugw
        #Vlan
        kw_vlan ="@@vlan@@"
        rp_vlan = vlan
        #Backup
        kw_njbuvpn = "@@njbuvpn@@"
        rp_njbuvpn = njbuvpn_tunnel_no_cidr
        kw_txbuvpn = "@@txbuvpn@@"  
        rp_txbuvpn = txbuvpn_tunnel_no_cidr
        kw_njbuvpn_cidr = "@@njbuvpn_cidr@@"
        rp_njbuvpn_cidr =nj_buvpn_tunnel
        kw_txbuvpn_cidr = "@@txbuvpn_cidr@@"
        rp_txbuvpn_cidr =tx_buvpn_tunnel
        kw_njbuvpn_1= "@@backup_nj_tunnel1incr@@"
        rp_njbuvpn_1=str(njbuvpn_tunn_incr_one)
        kw_txbuvpn_1="@@backup_tx_tunnel1incr@@"
        rp_txbuvpn_1=str(txbuvpn_tunn_incr_one)
        kw_njbuvpn_2= "@@njbuvpn2@@"
        rp_njbuvpn_2=njbuvpn_tunn_incr_two_cidr
        kw_txbuvpn_2="@@txbuvpn2@@"
        rp_txbuvpn_2=txbuvpn_tunn_incr_two_cidr
        #Office supernet subnetmask
        kw_osunet_subnetmask="@@subnetmask@@"
        rp_osunet_subnetmask=subnetmask
        #DCs
        kw_njdc3oc = "@@njdc3oc@@"
        rp_njdc3oc = njdc3oc
        kw_txdc3oc = "@@txdc3oc@@"
        rp_txdc3oc = txdc3oc
        kw_three_workstation = "@@3osnetworkstation@@"
        rp_three_workstation =threenetworkstation
        kw_three_voice = "@@3osvoice@@"
        rp_three_voice =threenetvoice
        kw_three_isolated = "@@3isolatednet@@"
        rp_three_isolated =threenetisolated

        #Juniper router02
        
        networkdevice ="E_2x_dia_rtr02.txt"
        shutil.copy("/mnt/win_share/builds/config_files/East/2_2x_DIA/" + networkdevice,"/mnt/win_share/config_backup/" + clientfullname + "/" + cid +"/"+ cid +"_" + region + "_" + networkdevice)
        #Replace
        fpc_client(clientfullname,cid,region,networkdevice)
        keywords_replace(kw_cid,rp_cid,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_region,rp_region,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_snmp,rp_snmp,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_psk,rp_psk,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_offsunetthree,rp_offsunetthree,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_oscidr,rp_oscidr,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_vlan,rp_vlan,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_budia,rp_budia,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_budia_mask,rp_budia_mask,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_budiagw,rp_budiagw,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njbuvpn_2,rp_njbuvpn_2,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txbuvpn_2,rp_txbuvpn_2,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njbuvpn,rp_njbuvpn,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txbuvpn,rp_txbuvpn,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njdc3oc,rp_njdc3oc,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txdc3oc,rp_txdc3oc,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njbuvpn_cidr,rp_njbuvpn_cidr,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txbuvpn_cidr,rp_txbuvpn_cidr,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_workstation,rp_three_workstation,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_voice,rp_three_voice,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_isolated,rp_three_isolated,cid,region,clientfullname,networkdevice)
        devicetype = "rtr02"
        add_host(devicetype,clientfullname,cid,region)
        add_CLI_networks_RTR(CLI_networks,cid,region,clientfullname,networkdevice)
        text_to_dos()
        #add_monitoring_east(devicetype,clientfullname,cid,region,rp_snmp)
        
        #GRE Tunnels Backup

        
        networkdevice = "E_dia_gre_tnl_rtrvpn02.txt"
        shutil.copy("/mnt/win_share/builds/config_files/East/2_2x_DIA/" + networkdevice,"/mnt/win_share/config_backup/" + clientfullname + "/" + cid +"/"+ cid +"_" + region + "_" + networkdevice)
        #Replace
        keywords_replace(kw_vlan,rp_vlan,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_cid,rp_cid,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_oscidr,rp_oscidr,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_offsunetthree,rp_offsunetthree,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_region,rp_region,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_budia,rp_budia,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_psk,rp_psk,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njbuvpn,rp_njbuvpn,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txbuvpn,rp_txbuvpn,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njbuvpn_1,rp_njbuvpn_1,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txbuvpn_1,rp_txbuvpn_1,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_osunet_subnetmask,rp_osunet_subnetmask,cid,region,clientfullname,networkdevice)
        text_to_dos()
    elif "5" in n:
        clear()
        print("Configuring East 5. L3 SW (Just L3 switch no router)")
        
        #Inputs
        officesupernet = input("Provide office supernet with subnetmask via CIDR notation Ex. 10.214.20.0/22 \n")
        njdc = input("Provide the NJDC network without subnet mask Ex. 10.121.20.0 \n")
        txdc = input("Provide the TXDC network without subnet mask Ex. 10.221.20.0 \n")

        #Ask CLI networks
        question_NW_CLI()
        p2p = input("Provide the P2P network with subnetmask via CIDR notation ex. 192.168.105.230/30 \n")


        #OfficeSupernet
        oscidr = officesupernet[-3:]
        subnetmask = cidr_to_netmask(officesupernet)[1]
        fourofficesupernet=officesupernet[:-3]
        threeofficesupernet = officesupernet[:-5]
         
        #Workstation
        officeworkstation = ipaddress.ip_address(fourofficesupernet) + 257
        workstation = str(officeworkstation)
        workstation = workstation[:-1] + "0"
        threenetworkstation = workstation[:-2]

        #Voice
        officevoice = ipaddress.ip_address(fourofficesupernet) + 513
        voice = str(officevoice)
        voice = voice[:-1] + "0"
        threenetvoice = voice[:-2]

        #Isolated
        officeisolated = ipaddress.ip_address(fourofficesupernet) + 771
        isolated = str(officeisolated)
        isolated = isolated[:-1] + "0"
        threenetisolated = isolated[:-2]

        
        #NJDC and TXDC
        njdc3oc = njdc[:-2]
        txdc3oc = txdc[:-2]



        #P2P
        p2p_no_cidr = p2p[:-3]
        p2p_only_cidr = p2p[-3:]
        p2p_increment_one = ipaddress.ip_address(str(p2p_no_cidr)) + 1
        p2p_increment_two = ipaddress.ip_address(str(p2p_no_cidr)) + 2
        p2p_increment_two_with_cidr = str(p2p_increment_two) + str(p2p_only_cidr)
        
        
        #Keywords and replacement
        kw_cid = "@@cid@@"
        rp_cid = cid
        kw_region = "@@region@@"
        rp_region = region
        kw_snmp = "@@snmp@@"
        rp_snmp = snmp_psk_generated()[0]
        kw_psk = "@@psk@@"
        rp_psk = snmp_psk_generated()[1]
        kw_offsunetthree = "@@3osnet@@"
        rp_offsunetthree = threeofficesupernet    
        kw_oscidr = "@@oscidr@@"
        rp_oscidr = oscidr
        kw_osunet_subnetmask="@@subnetmask@@"
        rp_osunet_subnetmask=subnetmask
        kw_p2p = "@@p2pog@@"
        rp_p2p =p2p_no_cidr
        kw_p2p_cidr= "@@p2pog_cidr@@"
        rp_p2p_cidr=p2p
        kw_p2pincr1 = "@@p2pdcside@@"
        rp_p2pincr1 = str(p2p_increment_one)
        kw_p2pincr2 ="@@p2pclientside@@"
        rp_p2pincr2 =str(p2p_increment_two_with_cidr)
        kw_njdc3oc = "@@njdc3oc@@"
        rp_njdc3oc = njdc3oc
        kw_txdc3oc = "@@txdc3oc@@"
        rp_txdc3oc = txdc3oc
        kw_three_workstation = "@@3osnetworkstation@@"
        rp_three_workstation =threenetworkstation
        kw_three_voice = "@@3osvoice@@"
        rp_three_voice =threenetvoice
        kw_three_isolated = "@@3isolatednet@@"
        rp_three_isolated =threenetisolated

        
        #Juniper switch01 24P and 48P
        
        networkdevice ="E_p2p_dia_sw01_24P.txt"
        shutil.copy("/mnt/win_share/builds/config_files/East/1_P2P_and_DIA/" + networkdevice,"/mnt/win_share/config_backup/" + clientfullname + "/" + cid +"/"+ cid +"_" + region + "_" + networkdevice)
        #Replace
        fpc_client(clientfullname,cid,region,networkdevice)
        keywords_replace(kw_cid,rp_cid,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_region,rp_region,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_snmp,rp_snmp,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_psk,rp_psk,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_offsunetthree,rp_offsunetthree,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_oscidr,rp_oscidr,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njdc3oc,rp_njdc3oc,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txdc3oc,rp_txdc3oc,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_p2pincr2,rp_p2pincr2,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_p2p,rp_p2p,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_workstation,rp_three_workstation,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_voice,rp_three_voice,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_isolated,rp_three_isolated,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_p2p_cidr,rp_p2p_cidr,cid,region,clientfullname,networkdevice)
        add_CLI_networks_L3SW(CLI_networks,cid,region,clientfullname,networkdevice)
        text_to_dos()
        networkdevice ="E_p2p_dia_sw01_48P.txt"
        shutil.copy("/mnt/win_share/builds/config_files/East/1_P2P_and_DIA/" + networkdevice,"/mnt/win_share/config_backup/" + clientfullname + "/" + cid +"/"+ cid +"_" + region + "_" + networkdevice)
        #Replace
        fpc_client(clientfullname,cid,region,networkdevice)
        keywords_replace(kw_cid,rp_cid,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_region,rp_region,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_snmp,rp_snmp,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_psk,rp_psk,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_offsunetthree,rp_offsunetthree,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_oscidr,rp_oscidr,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njdc3oc,rp_njdc3oc,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txdc3oc,rp_txdc3oc,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_p2pincr2,rp_p2pincr2,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_p2p,rp_p2p,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_workstation,rp_three_workstation,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_voice,rp_three_voice,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_isolated,rp_three_isolated,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_p2p_cidr,rp_p2p_cidr,cid,region,clientfullname,networkdevice)
        devicetype = "sw01"
        add_host(devicetype,clientfullname,cid,region)
        add_CLI_networks_L3SW(CLI_networks,cid,region,clientfullname,networkdevice)
        text_to_dos()
        #add_monitoring_east(devicetype,clientfullname,cid,region,rp_snmp)
    elif "6" in n:
        clear()
        print("Configuring East 6. L2 SW (Just L2 switch no router)")

        #Inputs
        officesupernet = input("Provide office supernet with subnetmask via CIDR notation Ex. 10.214.20.0/22 \n")    

        #OfficeSupernet
        oscidr = officesupernet[-3:]
        subnetmask = cidr_to_netmask(officesupernet)[1]
        fourofficesupernet=officesupernet[:-3]
        threeofficesupernet = officesupernet[:-5]
         
        #Workstation
        officeworkstation = ipaddress.ip_address(fourofficesupernet) + 257
        workstation = str(officeworkstation)
        workstation = workstation[:-1] + "0"
        threenetworkstation = workstation[:-2]

        #Voice
        officevoice = ipaddress.ip_address(fourofficesupernet) + 513
        voice = str(officevoice)
        voice = voice[:-1] + "0"
        threenetvoice = voice[:-2]

        #Isolated
        officeisolated = ipaddress.ip_address(fourofficesupernet) + 771
        isolated = str(officeisolated)
        isolated = isolated[:-1] + "0"
        threenetisolated = isolated[:-2]


        #Keywords and replacement
        kw_cid = "@@cid@@"
        rp_cid = cid
        kw_region = "@@region@@"
        rp_region = region
        kw_snmp = "@@snmp@@"
        rp_snmp = snmp_psk_generated()[0]
        kw_psk = "@@psk@@"
        rp_psk = snmp_psk_generated()[1]
        kw_offsunetthree = "@@3osnet@@"
        rp_offsunetthree = threeofficesupernet    
        kw_oscidr = "@@oscidr@@"
        rp_oscidr = oscidr
        #Office supernet subnetmask
        kw_osunet_subnetmask="@@subnetmask@@"
        rp_osunet_subnetmask=subnetmask
        kw_three_workstation = "@@3osnetworkstation@@"
        rp_three_workstation =threenetworkstation
        kw_three_voice = "@@3osvoice@@"
        rp_three_voice =threenetvoice
        kw_three_isolated = "@@3isolatednet@@"
        rp_three_isolated =threenetisolated

        
        #Juniper switch01 24P and 48P
        
        networkdevice ="E_2x_dia_sw01_24P.txt"
        shutil.copy("/mnt/win_share/builds/config_files/East/2_2x_DIA/" + networkdevice,"/mnt/win_share/config_backup/" + clientfullname + "/" + cid +"/"+ cid +"_" + region + "_" + networkdevice)
        #Replace
        keywords_replace(kw_cid,rp_cid,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_region,rp_region,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_snmp,rp_snmp,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_psk,rp_psk,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_offsunetthree,rp_offsunetthree,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_oscidr,rp_oscidr,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_workstation,rp_three_workstation,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_voice,rp_three_voice,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_isolated,rp_three_isolated,cid,region,clientfullname,networkdevice)
        text_to_dos()
        
        networkdevice ="E_2x_dia_sw01_48P.txt"
        shutil.copy("/mnt/win_share/builds/config_files/East/2_2x_DIA/" + networkdevice,"/mnt/win_share/config_backup/" + clientfullname + "/" + cid +"/"+ cid +"_" + region + "_" + networkdevice)
        #Replace
        keywords_replace(kw_cid,rp_cid,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_region,rp_region,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_snmp,rp_snmp,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_psk,rp_psk,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_offsunetthree,rp_offsunetthree,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_oscidr,rp_oscidr,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_workstation,rp_three_workstation,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_voice,rp_three_voice,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_isolated,rp_three_isolated,cid,region,clientfullname,networkdevice)
        devicetype = "sw01"
        add_host(devicetype,clientfullname,cid,region)
        text_to_dos()
        #add_monitoring_east(devicetype,clientfullname,cid,region,rp_snmp)
    else:
        print("Invalid input")
if "w" in eow:
    print("""
                   West Coast Chosen

        1. P2P and DIA (Full config L3 switch and router02) 
        2. 2x DIA (Full config L2 switch with router01 and 02)
        3. 1x DIA RTR01 (Full config L2 switch and router01)
        4. 1x DIA RTR02 (Just router 02 for L2 switch no switch)
        5. L3 SW (Just L3 switch no router)
        6. L2 SW (Just L2 switch no router)    
    """)
    
    n = input("Choose config setup between 1 to 6\n")
    if "1" in n:
        clear()
        print("Configuring West 1. P2P and DIA (Full config L3 switch and router02)\n")
        
        #Inputs
        officesupernet = input("Provide office supernet with subnetmask via CIDR notation Ex. 10.214.20.0/22 \n")
        njdc = input("Provide the SFDC network without subnet mask Ex. 10.121.20.0 \n")
        txdc = input("Provide the TXDC network without subnet mask Ex. 10.221.20.0 \n")
        vlan = input("Provide the vlan of the SFDC/TXDC servers Ex.3742 \n")
        nj_buvpn_tunnel = input("Provide the SF Backup VPN with subnet mask via CIDR notation Ex.192.168.105.10/30 \n")
        tx_buvpn_tunnel = input("Provide the TX Backup VPN with subnet mask via CIDR notation Ex.192.168.212.10/30 \n")

        #ADD_CLI
        question_NW_CLI()
        p2p = input("Provide the P2P network with subnetmask via CIDR notation ex. 192.168.105.230/30 \n")
        budia = input("Provide the Backup DIA with subnet mask via CIDR notation Ex.68.20.20.20/29 \n")
        bugw = input("Provide the Backup DIA Gateway without subnet mask \n")

        #OfficeSupernet
        oscidr = officesupernet[-3:]
        subnetmask = cidr_to_netmask(officesupernet)[1]
        fourofficesupernet=officesupernet[:-3]
        threeofficesupernet = officesupernet[:-5]
         
        #Workstation
        officeworkstation = ipaddress.ip_address(fourofficesupernet) + 257
        workstation = str(officeworkstation)
        workstation = workstation[:-1] + "0"
        threenetworkstation = workstation[:-2]

        #Voice
        officevoice = ipaddress.ip_address(fourofficesupernet) + 513
        voice = str(officevoice)
        voice = voice[:-1] + "0"
        threenetvoice = voice[:-2]

        #Isolated
        officeisolated = ipaddress.ip_address(fourofficesupernet) + 771
        isolated = str(officeisolated)
        isolated = isolated[:-1] + "0"
        threenetisolated = isolated[:-2]

        #Backup_DIA
        budia_mask = budia
        budia_wan = budia[:-3]
        
        #NJDC and TXDC
        njdc3oc = njdc[:-2]
        txdc3oc = txdc[:-2]

        #GRE Tunnels NJ and TX Backup
        njbuvpn_tunnel_no_cidr = nj_buvpn_tunnel[:-3]
        njbuvpn_tunnel_only_cidr = nj_buvpn_tunnel[-3:]
        txbuvpn_tunnel_no_cidr = tx_buvpn_tunnel[:-3]
        txbuvpn_tunnel_only_cidr =tx_buvpn_tunnel[-3:]

        njbuvpn_tunn_incr_two = ipaddress.ip_address(str(njbuvpn_tunnel_no_cidr)) + 2
        njbuvpn_tunn_incr_two_cidr = str(njbuvpn_tunn_incr_two) + str(njbuvpn_tunnel_only_cidr)
        
        txbuvpn_tunn_incr_two = ipaddress.ip_address(str(txbuvpn_tunnel_no_cidr)) + 2
        txbuvpn_tunn_incr_two_cidr = str(txbuvpn_tunn_incr_two) + str(txbuvpn_tunnel_only_cidr)
        
                
        njbuvpn_tunn_incr_one = ipaddress.ip_address(str(njbuvpn_tunnel_no_cidr)) + 1
        txbuvpn_tunn_incr_one = ipaddress.ip_address(str(txbuvpn_tunnel_no_cidr)) + 1

        #P2P
        p2p_no_cidr = p2p[:-3]
        p2p_only_cidr = p2p[-3:]
        p2p_increment_one = ipaddress.ip_address(str(p2p_no_cidr)) + 1
        p2p_increment_two = ipaddress.ip_address(str(p2p_no_cidr)) + 2
        p2p_increment_two_with_cidr = str(p2p_increment_two) + str(p2p_only_cidr)
        
        
        #Keywords and replacement
        kw_cid = "@@cid@@"
        rp_cid = cid
        kw_region = "@@region@@"
        rp_region = region
        kw_snmp = "@@snmp@@"
        rp_snmp = snmp_psk_generated()[0]
        kw_psk = "@@psk@@"
        rp_psk = snmp_psk_generated()[1]
        kw_offsunetthree = "@@3osnet@@"
        rp_offsunetthree = threeofficesupernet    
        kw_oscidr = "@@oscidr@@"
        rp_oscidr = oscidr
        kw_budia = "@@budia@@"
        rp_budia = budia_wan 
        kw_budia_mask = "@@budia_mask@@"
        rp_budia_mask = budia_mask
        kw_budiagw = "@@budiagw@@"
        rp_budiagw = bugw
        kw_vlan ="@@vlan@@"
        rp_vlan = vlan
        kw_njbuvpn = "@@njbuvpn@@"
        rp_njbuvpn = njbuvpn_tunnel_no_cidr
        kw_txbuvpn = "@@txbuvpn@@"  
        rp_txbuvpn = txbuvpn_tunnel_no_cidr
        kw_njbuvpn_cidr = "@@njbuvpn_cidr@@"
        rp_njbuvpn_cidr =nj_buvpn_tunnel
        kw_txbuvpn_cidr = "@@txbuvpn_cidr@@"
        rp_txbuvpn_cidr =tx_buvpn_tunnel
        kw_njbuvpn_1= "@@backup_nj_tunnel1incr@@"
        rp_njbuvpn_1=str(njbuvpn_tunn_incr_one)
        kw_txbuvpn_1="@@backup_tx_tunnel1incr@@"
        rp_txbuvpn_1=str(txbuvpn_tunn_incr_one)
        kw_njbuvpn_2= "@@njbuvpn2@@"
        rp_njbuvpn_2=njbuvpn_tunn_incr_two_cidr
        kw_txbuvpn_2="@@txbuvpn2@@"
        rp_txbuvpn_2=txbuvpn_tunn_incr_two_cidr
        kw_osunet_subnetmask="@@subnetmask@@"
        rp_osunet_subnetmask=subnetmask
        kw_p2p = "@@p2pog@@"
        rp_p2p =p2p_no_cidr
        kw_p2p_cidr= "@@p2pog_cidr@@"
        rp_p2p_cidr=p2p
        kw_p2pincr1 = "@@p2pdcside@@"
        rp_p2pincr1 = str(p2p_increment_one)
        kw_p2pincr2 ="@@p2pclientside@@"
        rp_p2pincr2 =str(p2p_increment_two_with_cidr)
        kw_njdc3oc = "@@njdc3oc@@"
        rp_njdc3oc = njdc3oc
        kw_txdc3oc = "@@txdc3oc@@"
        rp_txdc3oc = txdc3oc
        kw_three_workstation = "@@3osnetworkstation@@"
        rp_three_workstation =threenetworkstation
        kw_three_voice = "@@3osvoice@@"
        rp_three_voice =threenetvoice
        kw_three_isolated = "@@3isolatednet@@"
        rp_three_isolated =threenetisolated
        
        #Juniper router02
        
        networkdevice ="W_p2p_dia_rtr02.txt"
        shutil.copy("/mnt/win_share/builds/config_files/West/1_P2P_and_DIA/" + networkdevice,"/mnt/win_share/config_backup/" + clientfullname + "/" + cid +"/"+ cid +"_" + region + "_" + networkdevice)
        #Replace
        keywords_replace(kw_cid,rp_cid,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_region,rp_region,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_snmp,rp_snmp,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_psk,rp_psk,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_offsunetthree,rp_offsunetthree,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_oscidr,rp_oscidr,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_vlan,rp_vlan,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_budia,rp_budia,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_budia_mask,rp_budia_mask,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_budiagw,rp_budiagw,cid,region,clientfullname,networkdevice) 
        keywords_replace(kw_njbuvpn_2,rp_njbuvpn_2,cid,region,clientfullname,networkdevice) 
        keywords_replace(kw_txbuvpn_2,rp_txbuvpn_2,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njbuvpn,rp_njbuvpn,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txbuvpn,rp_txbuvpn,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njdc3oc,rp_njdc3oc,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txdc3oc,rp_txdc3oc,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njbuvpn_cidr,rp_njbuvpn_cidr,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txbuvpn_cidr,rp_txbuvpn_cidr,cid,region,clientfullname,networkdevice)
        devicetype = "rtr02"
        add_host(devicetype,clientfullname,cid,region)
        add_CLI_networks_RTR(CLI_networks,cid,region,clientfullname,networkdevice)
        text_to_dos()
        #add_monitoring_west(devicetype,clientfullname,cid,region,rp_snmp)
        #Juniper switch01 24P and 48P
        
        networkdevice ="W_p2p_dia_sw01_24P.txt"
        shutil.copy("/mnt/win_share/builds/config_files/West/1_P2P_and_DIA/" + networkdevice,"/mnt/win_share/config_backup/" + clientfullname + "/" + cid +"/"+ cid +"_" + region + "_" + networkdevice)
        #Replace
        fpc_client(clientfullname,cid,region,networkdevice)
        keywords_replace(kw_cid,rp_cid,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_region,rp_region,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_snmp,rp_snmp,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_psk,rp_psk,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_offsunetthree,rp_offsunetthree,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_oscidr,rp_oscidr,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_vlan,rp_vlan,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_budia,rp_budia,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_budia_mask,rp_budia_mask,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_budiagw,rp_budiagw,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njdc3oc,rp_njdc3oc,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txdc3oc,rp_txdc3oc,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_p2pincr2,rp_p2pincr2,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_p2p,rp_p2p,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_workstation,rp_three_workstation,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_voice,rp_three_voice,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_isolated,rp_three_isolated,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_p2p_cidr,rp_p2p_cidr,cid,region,clientfullname,networkdevice)
        add_CLI_networks_L3SW(CLI_networks,cid,region,clientfullname,networkdevice)
        text_to_dos()
        networkdevice ="W_p2p_dia_sw01_48P.txt"
        shutil.copy("/mnt/win_share/builds/config_files/West/1_P2P_and_DIA/" + networkdevice,"/mnt/win_share/config_backup/" + clientfullname + "/" + cid +"/"+ cid +"_" + region + "_" + networkdevice)
        #Replace
        fpc_client(clientfullname,cid,region,networkdevice)
        keywords_replace(kw_cid,rp_cid,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_region,rp_region,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_snmp,rp_snmp,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_psk,rp_psk,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_offsunetthree,rp_offsunetthree,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_oscidr,rp_oscidr,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_vlan,rp_vlan,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_budia,rp_budia,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_budia_mask,rp_budia_mask,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_budiagw,rp_budiagw,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njdc3oc,rp_njdc3oc,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txdc3oc,rp_txdc3oc,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_p2pincr2,rp_p2pincr2,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_p2p,rp_p2p,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_workstation,rp_three_workstation,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_voice,rp_three_voice,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_isolated,rp_three_isolated,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_p2p_cidr,rp_p2p_cidr,cid,region,clientfullname,networkdevice)
        devicetype = "sw01"
        add_host(devicetype,clientfullname,cid,region)
        add_CLI_networks_L3SW(CLI_networks,cid,region,clientfullname,networkdevice)
        text_to_dos()
        #add_monitoring_west(devicetype,clientfullname,cid,region,rp_snmp)
        #GRE Tunnels
        
        networkdevice = "W_p2p_dia_gre_tnl_rtrvpn02.txt"
        shutil.copy("/mnt/win_share/builds/config_files/West/1_P2P_and_DIA/" + networkdevice,"/mnt/win_share/config_backup/" + clientfullname + "/" + cid +"/"+ cid +"_" + region + "_" + networkdevice)
        #Replace
        keywords_replace(kw_vlan,rp_vlan,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_cid,rp_cid,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_oscidr,rp_oscidr,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_offsunetthree,rp_offsunetthree,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_region,rp_region,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_budia,rp_budia,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_psk,rp_psk,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njbuvpn,rp_njbuvpn,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txbuvpn,rp_txbuvpn,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njbuvpn_1,rp_njbuvpn_1,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txbuvpn_1,rp_txbuvpn_1,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_osunet_subnetmask,rp_osunet_subnetmask,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_p2p,rp_p2p,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_p2pincr1,rp_p2pincr1,cid,region,clientfullname,networkdevice)
        text_to_dos()
    elif "2" in n:
        clear()
        print("Configuring West 2. 2x DIA (Full config L2 switch with router01 and 02)")

        #Inputs
        officesupernet = input("Provide office supernet with subnetmask via CIDR notation Ex. 10.214.20.0/22 \n")
        njdc = input("Provide the SFDC network without subnet mask Ex. 10.121.20.0 \n")
        txdc = input("Provide the TXDC network without subnet mask Ex. 10.221.20.0 \n")
        vlan = input("Provide the vlan of the SFDC/TXDC servers Ex.3742 \n")
        nj_prvpn_tunnel = input("Provide the SF Primary VPN with subnet mask via CIDR notation Ex.192.168.105.10/30 \n")
        tx_prvpn_tunnel = input("Provide the TX Primary VPN with subnet mask via CIDR notation Ex.192.168.212.10/30 \n")        
        nj_buvpn_tunnel = input("Provide the SF Backup  VPN with subnet mask via CIDR notation Ex.192.168.105.10/30 \n")
        tx_buvpn_tunnel = input("Provide the TX Backup  VPN with subnet mask via CIDR notation Ex.192.168.212.10/30 \n")

        #Ask CLI networks
        question_NW_CLI()
        prdia = input("Provide the Primary DIA with subnet mask via CIDR notation Ex.68.20.20.20/29 \n")
        prgw = input("Provide the Primary DIA Gateway without subnet mask \n")
        budia = input("Provide the Backup  DIA with subnet mask via CIDR notation Ex.68.20.20.20/29 \n")
        bugw = input("Provide the Backup  DIA Gateway without subnet mask \n")

        #OfficeSupernet
        oscidr = officesupernet[-3:]
        subnetmask = cidr_to_netmask(officesupernet)[1]
        fourofficesupernet=officesupernet[:-3]
        threeofficesupernet = officesupernet[:-5]
         
        #Workstation
        officeworkstation = ipaddress.ip_address(fourofficesupernet) + 257
        workstation = str(officeworkstation)
        workstation = workstation[:-1] + "0"
        threenetworkstation = workstation[:-2]

        #Voice
        officevoice = ipaddress.ip_address(fourofficesupernet) + 513
        voice = str(officevoice)
        voice = voice[:-1] + "0"
        threenetvoice = voice[:-2]

        #Isolated
        officeisolated = ipaddress.ip_address(fourofficesupernet) + 771
        isolated = str(officeisolated)
        isolated = isolated[:-1] + "0"
        threenetisolated = isolated[:-2]

        #Primary DIA
        prdia_mask = prdia
        prdia_wan = prdia[:-3]

        #Backup_DIA
        budia_mask = budia
        budia_wan = budia[:-3]
        
        #NJDC and TXDC
        njdc3oc = njdc[:-2]
        txdc3oc = txdc[:-2]


        #GRE Tunnels NJ and TX Primary
        njprvpn_tunnel_no_cidr = nj_prvpn_tunnel[:-3]
        njprvpn_tunnel_only_cidr = nj_prvpn_tunnel[-3:]
        txprvpn_tunnel_no_cidr = tx_prvpn_tunnel[:-3]
        txprvpn_tunnel_only_cidr =tx_prvpn_tunnel[-3:]

        njprvpn_tunn_incr_two = ipaddress.ip_address(str(njprvpn_tunnel_no_cidr)) + 2
        njprvpn_tunn_incr_two_cidr = str(njprvpn_tunn_incr_two) + str(njprvpn_tunnel_only_cidr)
        
        txprvpn_tunn_incr_two = ipaddress.ip_address(str(txprvpn_tunnel_no_cidr)) + 2
        txprvpn_tunn_incr_two_cidr = str(txprvpn_tunn_incr_two) + str(txprvpn_tunnel_only_cidr)
        
                
        njprvpn_tunn_incr_one = ipaddress.ip_address(str(njprvpn_tunnel_no_cidr)) + 1
        txprvpn_tunn_incr_one = ipaddress.ip_address(str(txprvpn_tunnel_no_cidr)) + 1

        #GRE Tunnels NJ and TX Backup
        njbuvpn_tunnel_no_cidr = nj_buvpn_tunnel[:-3]
        njbuvpn_tunnel_only_cidr = nj_buvpn_tunnel[-3:]
        txbuvpn_tunnel_no_cidr = tx_buvpn_tunnel[:-3]
        txbuvpn_tunnel_only_cidr =tx_buvpn_tunnel[-3:]

        njbuvpn_tunn_incr_two = ipaddress.ip_address(str(njbuvpn_tunnel_no_cidr)) + 2
        njbuvpn_tunn_incr_two_cidr = str(njbuvpn_tunn_incr_two) + str(njbuvpn_tunnel_only_cidr)
        
        txbuvpn_tunn_incr_two = ipaddress.ip_address(str(txbuvpn_tunnel_no_cidr)) + 2
        txbuvpn_tunn_incr_two_cidr = str(txbuvpn_tunn_incr_two) + str(txbuvpn_tunnel_only_cidr)
        
                
        njbuvpn_tunn_incr_one = ipaddress.ip_address(str(njbuvpn_tunnel_no_cidr)) + 1
        txbuvpn_tunn_incr_one = ipaddress.ip_address(str(txbuvpn_tunnel_no_cidr)) + 1

        #Keywords and replacement
        kw_cid = "@@cid@@"
        rp_cid = cid
        kw_region = "@@region@@"
        rp_region = region
        kw_snmp = "@@snmp@@"
        rp_snmp = snmp_psk_generated()[0]
        kw_psk = "@@psk@@"
        rp_psk = snmp_psk_generated()[1]
        kw_offsunetthree = "@@3osnet@@"
        rp_offsunetthree = threeofficesupernet    
        kw_oscidr = "@@oscidr@@"
        rp_oscidr = oscidr
        #Primary DIA
        kw_prdia = "@@prdia@@"
        rp_prdia = prdia_wan 
        kw_prdia_mask = "@@prdia_mask@@"
        rp_prdia_mask = prdia_mask
        kw_prdiagw = "@@prdiagw@@"
        rp_prdiagw = prgw
        #Backup DIA
        kw_budia = "@@budia@@"
        rp_budia = budia_wan 
        kw_budia_mask = "@@budia_mask@@"
        rp_budia_mask = budia_mask
        kw_budiagw = "@@budiagw@@"
        rp_budiagw = bugw
        #Vlan
        kw_vlan ="@@vlan@@"
        rp_vlan = vlan
        #Primary
        kw_njprvpn = "@@njprvpn@@"
        rp_njprvpn = njprvpn_tunnel_no_cidr
        kw_txprvpn = "@@txprvpn@@"  
        rp_txprvpn = txprvpn_tunnel_no_cidr
        kw_njprvpn_cidr = "@@njprvpn_cidr@@"
        rp_njprvpn_cidr =nj_prvpn_tunnel
        kw_txprvpn_cidr = "@@txprvpn_cidr@@"
        rp_txprvpn_cidr =tx_prvpn_tunnel
        kw_njprvpn_1= "@@primary_nj_tunnel1incr@@"
        rp_njprvpn_1=str(njprvpn_tunn_incr_one)
        kw_txprvpn_1="@@primary_tx_tunnel1incr@@"
        rp_txprvpn_1=str(txprvpn_tunn_incr_one)
        kw_njprvpn_2= "@@njprvpn2@@"
        rp_njprvpn_2=njprvpn_tunn_incr_two_cidr
        kw_txprvpn_2="@@txprvpn2@@"
        rp_txprvpn_2=txprvpn_tunn_incr_two_cidr
        #Backup
        kw_njbuvpn = "@@njbuvpn@@"
        rp_njbuvpn = njbuvpn_tunnel_no_cidr
        kw_txbuvpn = "@@txbuvpn@@"  
        rp_txbuvpn = txbuvpn_tunnel_no_cidr
        kw_njbuvpn_cidr = "@@njbuvpn_cidr@@"
        rp_njbuvpn_cidr =nj_buvpn_tunnel
        kw_txbuvpn_cidr = "@@txbuvpn_cidr@@"
        rp_txbuvpn_cidr =tx_buvpn_tunnel
        kw_njbuvpn_1= "@@backup_nj_tunnel1incr@@"
        rp_njbuvpn_1=str(njbuvpn_tunn_incr_one)
        kw_txbuvpn_1="@@backup_tx_tunnel1incr@@"
        rp_txbuvpn_1=str(txbuvpn_tunn_incr_one)
        kw_njbuvpn_2= "@@njbuvpn2@@"
        rp_njbuvpn_2=njbuvpn_tunn_incr_two_cidr
        kw_txbuvpn_2="@@txbuvpn2@@"
        rp_txbuvpn_2=txbuvpn_tunn_incr_two_cidr
        #Office supernet subnetmask
        kw_osunet_subnetmask="@@subnetmask@@"
        rp_osunet_subnetmask=subnetmask
        #DCs
        kw_njdc3oc = "@@njdc3oc@@"
        rp_njdc3oc = njdc3oc
        kw_txdc3oc = "@@txdc3oc@@"
        rp_txdc3oc = txdc3oc
        kw_three_workstation = "@@3osnetworkstation@@"
        rp_three_workstation =threenetworkstation
        kw_three_voice = "@@3osvoice@@"
        rp_three_voice =threenetvoice
        kw_three_isolated = "@@3isolatednet@@"
        rp_three_isolated =threenetisolated

        #Juniper router01
        
        networkdevice ="W_2x_dia_rtr01.txt"
        shutil.copy("/mnt/win_share/builds/config_files/West/2_2x_DIA/" + networkdevice,"/mnt/win_share/config_backup/" + clientfullname + "/" + cid +"/"+ cid +"_" + region + "_" + networkdevice)
        #Replace
        fpc_client(clientfullname,cid,region,networkdevice)
        keywords_replace(kw_cid,rp_cid,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_region,rp_region,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_snmp,rp_snmp,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_psk,rp_psk,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_offsunetthree,rp_offsunetthree,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_oscidr,rp_oscidr,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_vlan,rp_vlan,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_prdia,rp_prdia,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_prdia_mask,rp_prdia_mask,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_prdiagw,rp_prdiagw,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njprvpn_2,rp_njprvpn_2,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txprvpn_2,rp_txprvpn_2,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njprvpn,rp_njprvpn,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txprvpn,rp_txprvpn,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njdc3oc,rp_njdc3oc,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txdc3oc,rp_txdc3oc,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njprvpn_cidr,rp_njprvpn_cidr,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txprvpn_cidr,rp_txprvpn_cidr,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_workstation,rp_three_workstation,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_voice,rp_three_voice,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_isolated,rp_three_isolated,cid,region,clientfullname,networkdevice)
        devicetype = "rtr01"
        add_host(devicetype,clientfullname,cid,region)
        add_CLI_networks_RTR(CLI_networks,cid,region,clientfullname,networkdevice)
        text_to_dos()
        #add_monitoring_west(devicetype,clientfullname,cid,region,rp_snmp)
        #Juniper router02
        
        networkdevice ="W_2x_dia_rtr02.txt"
        shutil.copy("/mnt/win_share/builds/config_files/West/2_2x_DIA/" + networkdevice,"/mnt/win_share/config_backup/" + clientfullname + "/" + cid +"/"+ cid +"_" + region + "_" + networkdevice)
        #Replace
        fpc_client(clientfullname,cid,region,networkdevice)
        keywords_replace(kw_cid,rp_cid,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_region,rp_region,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_snmp,rp_snmp,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_psk,rp_psk,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_offsunetthree,rp_offsunetthree,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_oscidr,rp_oscidr,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_vlan,rp_vlan,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_budia,rp_budia,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_budia_mask,rp_budia_mask,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_budiagw,rp_budiagw,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njbuvpn_2,rp_njbuvpn_2,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txbuvpn_2,rp_txbuvpn_2,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njbuvpn,rp_njbuvpn,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txbuvpn,rp_txbuvpn,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njdc3oc,rp_njdc3oc,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txdc3oc,rp_txdc3oc,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njbuvpn_cidr,rp_njbuvpn_cidr,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txbuvpn_cidr,rp_txbuvpn_cidr,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_workstation,rp_three_workstation,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_voice,rp_three_voice,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_isolated,rp_three_isolated,cid,region,clientfullname,networkdevice)
        devicetype = "rtr02"
        add_host(devicetype,clientfullname,cid,region)
        add_CLI_networks_RTR(CLI_networks,cid,region,clientfullname,networkdevice)
        text_to_dos()
        #add_monitoring_west(devicetype,clientfullname,cid,region,rp_snmp)
        #Juniper switch01 24P and 48P
        
        networkdevice ="W_2x_dia_sw01_24P.txt"
        shutil.copy("/mnt/win_share/builds/config_files/West/2_2x_DIA/" + networkdevice,"/mnt/win_share/config_backup/" + clientfullname + "/" + cid +"/"+ cid +"_" + region + "_" + networkdevice)
        #Replace
        keywords_replace(kw_cid,rp_cid,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_region,rp_region,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_snmp,rp_snmp,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_psk,rp_psk,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_offsunetthree,rp_offsunetthree,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_oscidr,rp_oscidr,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njdc3oc,rp_njdc3oc,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txdc3oc,rp_txdc3oc,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_workstation,rp_three_workstation,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_voice,rp_three_voice,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_isolated,rp_three_isolated,cid,region,clientfullname,networkdevice)
        text_to_dos()
        
        
        networkdevice ="W_2x_dia_sw01_48P.txt"
        shutil.copy("/mnt/win_share/builds/config_files/West/2_2x_DIA/" + networkdevice,"/mnt/win_share/config_backup/" + clientfullname + "/" + cid +"/"+ cid +"_" + region + "_" + networkdevice)
        #Replace
        keywords_replace(kw_cid,rp_cid,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_region,rp_region,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_snmp,rp_snmp,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_psk,rp_psk,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_offsunetthree,rp_offsunetthree,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_oscidr,rp_oscidr,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njdc3oc,rp_njdc3oc,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txdc3oc,rp_txdc3oc,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_workstation,rp_three_workstation,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_voice,rp_three_voice,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_isolated,rp_three_isolated,cid,region,clientfullname,networkdevice)
        devicetype = "sw01"
        add_host(devicetype,clientfullname,cid,region)
        text_to_dos()
        #add_monitoring_west(devicetype,clientfullname,cid,region,rp_snmp)
        
        #GRE Tunnels Primary and Backup


        networkdevice = "W_dia_gre_tnl_rtrvpn01.txt"
        shutil.copy("/mnt/win_share/builds/config_files/West/2_2x_DIA/" + networkdevice,"/mnt/win_share/config_backup/" + clientfullname + "/" + cid +"/"+ cid +"_" + region + "_" + networkdevice)
        #Replace
        keywords_replace(kw_vlan,rp_vlan,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_cid,rp_cid,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_oscidr,rp_oscidr,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_offsunetthree,rp_offsunetthree,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_region,rp_region,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_prdia,rp_prdia,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_psk,rp_psk,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njprvpn,rp_njprvpn,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txprvpn,rp_txprvpn,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njprvpn_1,rp_njprvpn_1,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txprvpn_1,rp_txprvpn_1,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_osunet_subnetmask,rp_osunet_subnetmask,cid,region,clientfullname,networkdevice)
        text_to_dos()

        
        networkdevice = "W_dia_gre_tnl_rtrvpn02.txt"
        shutil.copy("/mnt/win_share/builds/config_files/West/2_2x_DIA/" + networkdevice,"/mnt/win_share/config_backup/" + clientfullname + "/" + cid +"/"+ cid +"_" + region + "_" + networkdevice)
        #Replace
        keywords_replace(kw_vlan,rp_vlan,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_cid,rp_cid,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_oscidr,rp_oscidr,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_offsunetthree,rp_offsunetthree,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_region,rp_region,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_budia,rp_budia,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_psk,rp_psk,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njbuvpn,rp_njbuvpn,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txbuvpn,rp_txbuvpn,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njbuvpn_1,rp_njbuvpn_1,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txbuvpn_1,rp_txbuvpn_1,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_osunet_subnetmask,rp_osunet_subnetmask,cid,region,clientfullname,networkdevice)
        text_to_dos()
    elif "3" in n:
        clear()
        print("Configuring West 3. 1x DIA RTR01 (Full config L2 switch and router01)")

        #Inputs
        officesupernet = input("Provide office supernet with subnetmask via CIDR notation Ex. 10.214.20.0/22 \n")
        njdc = input("Provide the SFDC network without subnet mask Ex. 10.121.20.0 \n")
        txdc = input("Provide the TXDC network without subnet mask Ex. 10.221.20.0 \n")
        vlan = input("Provide the vlan of the SFDC/TXDC servers Ex.3742 \n")
        nj_prvpn_tunnel = input("Provide the SF Primary VPN with subnet mask via CIDR notation Ex.192.168.105.10/30 \n")
        tx_prvpn_tunnel = input("Provide the TX Primary VPN with subnet mask via CIDR notation Ex.192.168.212.10/30 \n")  
      
        #Ask CLI networks
        question_NW_CLI()
        prdia = input("Provide the Primary DIA with subnet mask via CIDR notation Ex.68.20.20.20/29 \n")
        prgw = input("Provide the Primary DIA Gateway without subnet mask \n")

        #OfficeSupernet
        oscidr = officesupernet[-3:]
        subnetmask = cidr_to_netmask(officesupernet)[1]
        fourofficesupernet=officesupernet[:-3]
        threeofficesupernet = officesupernet[:-5]
         
        #Workstation
        officeworkstation = ipaddress.ip_address(fourofficesupernet) + 257
        workstation = str(officeworkstation)
        workstation = workstation[:-1] + "0"
        threenetworkstation = workstation[:-2]

        #Voice
        officevoice = ipaddress.ip_address(fourofficesupernet) + 513
        voice = str(officevoice)
        voice = voice[:-1] + "0"
        threenetvoice = voice[:-2]

        #Isolated
        officeisolated = ipaddress.ip_address(fourofficesupernet) + 771
        isolated = str(officeisolated)
        isolated = isolated[:-1] + "0"
        threenetisolated = isolated[:-2]

        #Primary DIA
        prdia_mask = prdia
        prdia_wan = prdia[:-3]

        
        #NJDC and TXDC
        njdc3oc = njdc[:-2]
        txdc3oc = txdc[:-2]


        #GRE Tunnels NJ and TX Primary
        njprvpn_tunnel_no_cidr = nj_prvpn_tunnel[:-3]
        njprvpn_tunnel_only_cidr = nj_prvpn_tunnel[-3:]
        txprvpn_tunnel_no_cidr = tx_prvpn_tunnel[:-3]
        txprvpn_tunnel_only_cidr =tx_prvpn_tunnel[-3:]

        njprvpn_tunn_incr_two = ipaddress.ip_address(str(njprvpn_tunnel_no_cidr)) + 2
        njprvpn_tunn_incr_two_cidr = str(njprvpn_tunn_incr_two) + str(njprvpn_tunnel_only_cidr)
        
        txprvpn_tunn_incr_two = ipaddress.ip_address(str(txprvpn_tunnel_no_cidr)) + 2
        txprvpn_tunn_incr_two_cidr = str(txprvpn_tunn_incr_two) + str(txprvpn_tunnel_only_cidr)
        
                
        njprvpn_tunn_incr_one = ipaddress.ip_address(str(njprvpn_tunnel_no_cidr)) + 1
        txprvpn_tunn_incr_one = ipaddress.ip_address(str(txprvpn_tunnel_no_cidr)) + 1


        #Keywords and replacement
        kw_cid = "@@cid@@"
        rp_cid = cid
        kw_region = "@@region@@"
        rp_region = region
        kw_snmp = "@@snmp@@"
        rp_snmp = snmp_psk_generated()[0]
        kw_psk = "@@psk@@"
        rp_psk = snmp_psk_generated()[1]
        kw_offsunetthree = "@@3osnet@@"
        rp_offsunetthree = threeofficesupernet    
        kw_oscidr = "@@oscidr@@"
        rp_oscidr = oscidr
        #Primary DIA
        kw_prdia = "@@prdia@@"
        rp_prdia = prdia_wan 
        kw_prdia_mask = "@@prdia_mask@@"
        rp_prdia_mask = prdia_mask
        kw_prdiagw = "@@prdiagw@@"
        rp_prdiagw = prgw
        #Vlan
        kw_vlan ="@@vlan@@"
        rp_vlan = vlan
        #Primary
        kw_njprvpn = "@@njprvpn@@"
        rp_njprvpn = njprvpn_tunnel_no_cidr
        kw_txprvpn = "@@txprvpn@@"  
        rp_txprvpn = txprvpn_tunnel_no_cidr
        kw_njprvpn_cidr = "@@njprvpn_cidr@@"
        rp_njprvpn_cidr =nj_prvpn_tunnel
        kw_txprvpn_cidr = "@@txprvpn_cidr@@"
        rp_txprvpn_cidr =tx_prvpn_tunnel
        kw_njprvpn_1= "@@primary_nj_tunnel1incr@@"
        rp_njprvpn_1=str(njprvpn_tunn_incr_one)
        kw_txprvpn_1="@@primary_tx_tunnel1incr@@"
        rp_txprvpn_1=str(txprvpn_tunn_incr_one)
        kw_njprvpn_2= "@@njprvpn2@@"
        rp_njprvpn_2=njprvpn_tunn_incr_two_cidr
        kw_txprvpn_2="@@txprvpn2@@"
        rp_txprvpn_2=txprvpn_tunn_incr_two_cidr
        #Office supernet subnetmask
        kw_osunet_subnetmask="@@subnetmask@@"
        rp_osunet_subnetmask=subnetmask
        #DCs
        kw_njdc3oc = "@@njdc3oc@@"
        rp_njdc3oc = njdc3oc
        kw_txdc3oc = "@@txdc3oc@@"
        rp_txdc3oc = txdc3oc
        kw_three_workstation = "@@3osnetworkstation@@"
        rp_three_workstation =threenetworkstation
        kw_three_voice = "@@3osvoice@@"
        rp_three_voice =threenetvoice
        kw_three_isolated = "@@3isolatednet@@"
        rp_three_isolated =threenetisolated

        #Juniper router01
        
        networkdevice ="W_2x_dia_rtr01.txt"
        shutil.copy("/mnt/win_share/builds/config_files/West/2_2x_DIA/" + networkdevice,"/mnt/win_share/config_backup/" + clientfullname + "/" + cid +"/"+ cid +"_" + region + "_" + networkdevice)
        #Replace
        fpc_client(clientfullname,cid,region,networkdevice)
        keywords_replace(kw_cid,rp_cid,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_region,rp_region,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_snmp,rp_snmp,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_psk,rp_psk,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_offsunetthree,rp_offsunetthree,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_oscidr,rp_oscidr,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_vlan,rp_vlan,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_prdia,rp_prdia,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_prdia_mask,rp_prdia_mask,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_prdiagw,rp_prdiagw,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njprvpn_2,rp_njprvpn_2,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txprvpn_2,rp_txprvpn_2,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njprvpn,rp_njprvpn,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txprvpn,rp_txprvpn,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njdc3oc,rp_njdc3oc,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txdc3oc,rp_txdc3oc,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njprvpn_cidr,rp_njprvpn_cidr,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txprvpn_cidr,rp_txprvpn_cidr,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_workstation,rp_three_workstation,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_voice,rp_three_voice,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_isolated,rp_three_isolated,cid,region,clientfullname,networkdevice)
        devicetype = "rtr01"
        add_host(devicetype,clientfullname,cid,region)
        add_CLI_networks_RTR(CLI_networks,cid,region,clientfullname,networkdevice)
        text_to_dos()
        #add_monitoring_west(devicetype,clientfullname,cid,region,rp_snmp)

        #Juniper switch01 24P and 48P
        
        networkdevice ="W_2x_dia_sw01_24P.txt"
        shutil.copy("/mnt/win_share/builds/config_files/West/2_2x_DIA/" + networkdevice,"/mnt/win_share/config_backup/" + clientfullname + "/" + cid +"/"+ cid +"_" + region + "_" + networkdevice)
        #Replace
        keywords_replace(kw_cid,rp_cid,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_region,rp_region,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_snmp,rp_snmp,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_psk,rp_psk,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_offsunetthree,rp_offsunetthree,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_oscidr,rp_oscidr,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njdc3oc,rp_njdc3oc,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txdc3oc,rp_txdc3oc,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_workstation,rp_three_workstation,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_voice,rp_three_voice,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_isolated,rp_three_isolated,cid,region,clientfullname,networkdevice)
        text_to_dos()
        
        
        networkdevice ="W_2x_dia_sw01_48P.txt"
        shutil.copy("/mnt/win_share/builds/config_files/West/2_2x_DIA/" + networkdevice,"/mnt/win_share/config_backup/" + clientfullname + "/" + cid +"/"+ cid +"_" + region + "_" + networkdevice)
        #Replace
        keywords_replace(kw_cid,rp_cid,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_region,rp_region,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_snmp,rp_snmp,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_psk,rp_psk,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_offsunetthree,rp_offsunetthree,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_oscidr,rp_oscidr,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njdc3oc,rp_njdc3oc,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txdc3oc,rp_txdc3oc,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_workstation,rp_three_workstation,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_voice,rp_three_voice,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_isolated,rp_three_isolated,cid,region,clientfullname,networkdevice)
        devicetype = "sw01"
        add_host(devicetype,clientfullname,cid,region)
        text_to_dos()
        #add_monitoring_west(devicetype,clientfullname,cid,region,rp_snmp)
        
        
        #GRE Tunnels Primary and Backup


        networkdevice = "W_dia_gre_tnl_rtrvpn01.txt"
        shutil.copy("/mnt/win_share/builds/config_files/West/2_2x_DIA/" + networkdevice,"/mnt/win_share/config_backup/" + clientfullname + "/" + cid +"/"+ cid +"_" + region + "_" + networkdevice)
        #Replace
        keywords_replace(kw_vlan,rp_vlan,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_cid,rp_cid,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_oscidr,rp_oscidr,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_offsunetthree,rp_offsunetthree,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_region,rp_region,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_prdia,rp_prdia,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_psk,rp_psk,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njprvpn,rp_njprvpn,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txprvpn,rp_txprvpn,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njprvpn_1,rp_njprvpn_1,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txprvpn_1,rp_txprvpn_1,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_osunet_subnetmask,rp_osunet_subnetmask,cid,region,clientfullname,networkdevice)
        text_to_dos()
    elif "4" in n:
        clear()
        print("Configuring West 4. 1x DIA RTR02 (Just router 02 for L2 switch no switch)")

        #Inputs
        officesupernet = input("Provide office supernet with subnetmask via CIDR notation Ex. 10.214.20.0/22 \n")
        njdc = input("Provide the SFDC network without subnet mask Ex. 10.121.20.0 \n")
        txdc = input("Provide the TXDC network without subnet mask Ex. 10.221.20.0 \n")
        vlan = input("Provide the vlan of the SFDC/TXDC servers Ex.3742 \n")       
        nj_buvpn_tunnel = input("Provide the SF Backup  VPN with subnet mask via CIDR notation Ex.192.168.105.10/30 \n")
        tx_buvpn_tunnel = input("Provide the TX Backup  VPN with subnet mask via CIDR notation Ex.192.168.212.10/30 \n")

        #Ask CLI networks
        question_NW_CLI()
        budia = input("Provide the Backup  DIA with subnet mask via CIDR notation Ex.68.20.20.20/29 \n")
        bugw = input("Provide the Backup  DIA Gateway without subnet mask \n")

        #OfficeSupernet
        oscidr = officesupernet[-3:]
        subnetmask = cidr_to_netmask(officesupernet)[1]
        fourofficesupernet=officesupernet[:-3]
        threeofficesupernet = officesupernet[:-5]
         
        #Workstation
        officeworkstation = ipaddress.ip_address(fourofficesupernet) + 257
        workstation = str(officeworkstation)
        workstation = workstation[:-1] + "0"
        threenetworkstation = workstation[:-2]

        #Voice
        officevoice = ipaddress.ip_address(fourofficesupernet) + 513
        voice = str(officevoice)
        voice = voice[:-1] + "0"
        threenetvoice = voice[:-2]

        #Isolated
        officeisolated = ipaddress.ip_address(fourofficesupernet) + 771
        isolated = str(officeisolated)
        isolated = isolated[:-1] + "0"
        threenetisolated = isolated[:-2]


        #Backup_DIA
        budia_mask = budia
        budia_wan = budia[:-3]
        
        #NJDC and TXDC
        njdc3oc = njdc[:-2]
        txdc3oc = txdc[:-2]



        #GRE Tunnels NJ and TX Backup
        njbuvpn_tunnel_no_cidr = nj_buvpn_tunnel[:-3]
        njbuvpn_tunnel_only_cidr = nj_buvpn_tunnel[-3:]
        txbuvpn_tunnel_no_cidr = tx_buvpn_tunnel[:-3]
        txbuvpn_tunnel_only_cidr =tx_buvpn_tunnel[-3:]

        njbuvpn_tunn_incr_two = ipaddress.ip_address(str(njbuvpn_tunnel_no_cidr)) + 2
        njbuvpn_tunn_incr_two_cidr = str(njbuvpn_tunn_incr_two) + str(njbuvpn_tunnel_only_cidr)
        
        txbuvpn_tunn_incr_two = ipaddress.ip_address(str(txbuvpn_tunnel_no_cidr)) + 2
        txbuvpn_tunn_incr_two_cidr = str(txbuvpn_tunn_incr_two) + str(txbuvpn_tunnel_only_cidr)
        
                
        njbuvpn_tunn_incr_one = ipaddress.ip_address(str(njbuvpn_tunnel_no_cidr)) + 1
        txbuvpn_tunn_incr_one = ipaddress.ip_address(str(txbuvpn_tunnel_no_cidr)) + 1

        #Keywords and replacement
        kw_cid = "@@cid@@"
        rp_cid = cid
        kw_region = "@@region@@"
        rp_region = region
        kw_snmp = "@@snmp@@"
        rp_snmp = snmp_psk_generated()[0]
        kw_psk = "@@psk@@"
        rp_psk = snmp_psk_generated()[1]
        kw_offsunetthree = "@@3osnet@@"
        rp_offsunetthree = threeofficesupernet    
        kw_oscidr = "@@oscidr@@"
        rp_oscidr = oscidr
        #Backup DIA
        kw_budia = "@@budia@@"
        rp_budia = budia_wan 
        kw_budia_mask = "@@budia_mask@@"
        rp_budia_mask = budia_mask
        kw_budiagw = "@@budiagw@@"
        rp_budiagw = bugw
        #Vlan
        kw_vlan ="@@vlan@@"
        rp_vlan = vlan
        #Backup
        kw_njbuvpn = "@@njbuvpn@@"
        rp_njbuvpn = njbuvpn_tunnel_no_cidr
        kw_txbuvpn = "@@txbuvpn@@"  
        rp_txbuvpn = txbuvpn_tunnel_no_cidr
        kw_njbuvpn_cidr = "@@njbuvpn_cidr@@"
        rp_njbuvpn_cidr =nj_buvpn_tunnel
        kw_txbuvpn_cidr = "@@txbuvpn_cidr@@"
        rp_txbuvpn_cidr =tx_buvpn_tunnel
        kw_njbuvpn_1= "@@backup_nj_tunnel1incr@@"
        rp_njbuvpn_1=str(njbuvpn_tunn_incr_one)
        kw_txbuvpn_1="@@backup_tx_tunnel1incr@@"
        rp_txbuvpn_1=str(txbuvpn_tunn_incr_one)
        kw_njbuvpn_2= "@@njbuvpn2@@"
        rp_njbuvpn_2=njbuvpn_tunn_incr_two_cidr
        kw_txbuvpn_2="@@txbuvpn2@@"
        rp_txbuvpn_2=txbuvpn_tunn_incr_two_cidr
        #Office supernet subnetmask
        kw_osunet_subnetmask="@@subnetmask@@"
        rp_osunet_subnetmask=subnetmask
        #DCs
        kw_njdc3oc = "@@njdc3oc@@"
        rp_njdc3oc = njdc3oc
        kw_txdc3oc = "@@txdc3oc@@"
        rp_txdc3oc = txdc3oc
        kw_three_workstation = "@@3osnetworkstation@@"
        rp_three_workstation =threenetworkstation
        kw_three_voice = "@@3osvoice@@"
        rp_three_voice =threenetvoice
        kw_three_isolated = "@@3isolatednet@@"
        rp_three_isolated =threenetisolated

        #Juniper router02
        
        networkdevice ="W_2x_dia_rtr02.txt"
        shutil.copy("/mnt/win_share/builds/config_files/West/2_2x_DIA/" + networkdevice,"/mnt/win_share/config_backup/" + clientfullname + "/" + cid +"/"+ cid +"_" + region + "_" + networkdevice)
        #Replace
        fpc_client(clientfullname,cid,region,networkdevice)
        keywords_replace(kw_cid,rp_cid,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_region,rp_region,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_snmp,rp_snmp,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_psk,rp_psk,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_offsunetthree,rp_offsunetthree,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_oscidr,rp_oscidr,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_vlan,rp_vlan,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_budia,rp_budia,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_budia_mask,rp_budia_mask,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_budiagw,rp_budiagw,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njbuvpn_2,rp_njbuvpn_2,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txbuvpn_2,rp_txbuvpn_2,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njbuvpn,rp_njbuvpn,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txbuvpn,rp_txbuvpn,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njdc3oc,rp_njdc3oc,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txdc3oc,rp_txdc3oc,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njbuvpn_cidr,rp_njbuvpn_cidr,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txbuvpn_cidr,rp_txbuvpn_cidr,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_workstation,rp_three_workstation,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_voice,rp_three_voice,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_isolated,rp_three_isolated,cid,region,clientfullname,networkdevice)
        devicetype = "rtr02"
        add_host(devicetype,clientfullname,cid,region)
        add_CLI_networks_RTR(CLI_networks,cid,region,clientfullname,networkdevice)
        text_to_dos()
        #add_monitoring_west(devicetype,clientfullname,cid,region,rp_snmp)
   
        
        #GRE Tunnels Backup

        
        networkdevice = "W_dia_gre_tnl_rtrvpn02.txt"
        shutil.copy("/mnt/win_share/builds/config_files/West/2_2x_DIA/" + networkdevice,"/mnt/win_share/config_backup/" + clientfullname + "/" + cid +"/"+ cid +"_" + region + "_" + networkdevice)
        #Replace
        keywords_replace(kw_vlan,rp_vlan,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_cid,rp_cid,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_oscidr,rp_oscidr,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_offsunetthree,rp_offsunetthree,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_region,rp_region,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_budia,rp_budia,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_psk,rp_psk,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njbuvpn,rp_njbuvpn,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txbuvpn,rp_txbuvpn,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njbuvpn_1,rp_njbuvpn_1,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txbuvpn_1,rp_txbuvpn_1,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_osunet_subnetmask,rp_osunet_subnetmask,cid,region,clientfullname,networkdevice)
        text_to_dos()
    elif "5" in n:
        clear()
        print("Configuring West 5. L3 SW (Just L3 switch no router)")
        
        #Inputs
        officesupernet = input("Provide office supernet with subnetmask via CIDR notation Ex. 10.214.20.0/22 \n")
        njdc = input("Provide the SFDC network without subnet mask Ex. 10.121.20.0 \n")
        txdc = input("Provide the TXDC network without subnet mask Ex. 10.221.20.0 \n")

        #Ask CLI networks
        question_NW_CLI()
        p2p = input("Provide the P2P network with subnetmask via CIDR notation ex. 192.168.105.230/30 \n")


        #OfficeSupernet
        oscidr = officesupernet[-3:]
        subnetmask = cidr_to_netmask(officesupernet)[1]
        fourofficesupernet=officesupernet[:-3]
        threeofficesupernet = officesupernet[:-5]
         
        #Workstation
        officeworkstation = ipaddress.ip_address(fourofficesupernet) + 257
        workstation = str(officeworkstation)
        workstation = workstation[:-1] + "0"
        threenetworkstation = workstation[:-2]

        #Voice
        officevoice = ipaddress.ip_address(fourofficesupernet) + 513
        voice = str(officevoice)
        voice = voice[:-1] + "0"
        threenetvoice = voice[:-2]

        #Isolated
        officeisolated = ipaddress.ip_address(fourofficesupernet) + 771
        isolated = str(officeisolated)
        isolated = isolated[:-1] + "0"
        threenetisolated = isolated[:-2]

        
        #NJDC and TXDC
        njdc3oc = njdc[:-2]
        txdc3oc = txdc[:-2]



        #P2P
        p2p_no_cidr = p2p[:-3]
        p2p_only_cidr = p2p[-3:]
        p2p_increment_one = ipaddress.ip_address(str(p2p_no_cidr)) + 1
        p2p_increment_two = ipaddress.ip_address(str(p2p_no_cidr)) + 2
        p2p_increment_two_with_cidr = str(p2p_increment_two) + str(p2p_only_cidr)
        
        
        #Keywords and replacement
        kw_cid = "@@cid@@"
        rp_cid = cid
        kw_region = "@@region@@"
        rp_region = region
        kw_snmp = "@@snmp@@"
        rp_snmp = snmp_psk_generated()[0]
        kw_psk = "@@psk@@"
        rp_psk = snmp_psk_generated()[1]
        kw_offsunetthree = "@@3osnet@@"
        rp_offsunetthree = threeofficesupernet    
        kw_oscidr = "@@oscidr@@"
        rp_oscidr = oscidr
        kw_osunet_subnetmask="@@subnetmask@@"
        rp_osunet_subnetmask=subnetmask
        kw_p2p = "@@p2pog@@"
        rp_p2p =p2p_no_cidr
        kw_p2p_cidr= "@@p2pog_cidr@@"
        rp_p2p_cidr=p2p
        kw_p2pincr1 = "@@p2pdcside@@"
        rp_p2pincr1 = str(p2p_increment_one)
        kw_p2pincr2 ="@@p2pclientside@@"
        rp_p2pincr2 =str(p2p_increment_two_with_cidr)
        kw_njdc3oc = "@@njdc3oc@@"
        rp_njdc3oc = njdc3oc
        kw_txdc3oc = "@@txdc3oc@@"
        rp_txdc3oc = txdc3oc
        kw_three_workstation = "@@3osnetworkstation@@"
        rp_three_workstation =threenetworkstation
        kw_three_voice = "@@3osvoice@@"
        rp_three_voice =threenetvoice
        kw_three_isolated = "@@3isolatednet@@"
        rp_three_isolated =threenetisolated

        
        #Juniper switch01 24P and 48P
        
        networkdevice ="W_p2p_dia_sw01_24P.txt"
        shutil.copy("/mnt/win_share/builds/config_files/West/1_P2P_and_DIA/" + networkdevice,"/mnt/win_share/config_backup/" + clientfullname + "/" + cid +"/"+ cid +"_" + region + "_" + networkdevice)
        #Replace
        fpc_client(clientfullname,cid,region,networkdevice)
        keywords_replace(kw_cid,rp_cid,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_region,rp_region,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_snmp,rp_snmp,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_psk,rp_psk,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_offsunetthree,rp_offsunetthree,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_oscidr,rp_oscidr,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njdc3oc,rp_njdc3oc,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txdc3oc,rp_txdc3oc,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_p2pincr2,rp_p2pincr2,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_p2p,rp_p2p,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_workstation,rp_three_workstation,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_voice,rp_three_voice,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_isolated,rp_three_isolated,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_p2p_cidr,rp_p2p_cidr,cid,region,clientfullname,networkdevice)
        add_CLI_networks_L3SW(CLI_networks,cid,region,clientfullname,networkdevice)
        text_to_dos()

        
        networkdevice ="W_p2p_dia_sw01_48P.txt"
        shutil.copy("/mnt/win_share/builds/config_files/West/1_P2P_and_DIA/" + networkdevice,"/mnt/win_share/config_backup/" + clientfullname + "/" + cid +"/"+ cid +"_" + region + "_" + networkdevice)
        #Replace
        fpc_client(clientfullname,cid,region,networkdevice)
        keywords_replace(kw_cid,rp_cid,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_region,rp_region,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_snmp,rp_snmp,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_psk,rp_psk,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_offsunetthree,rp_offsunetthree,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_oscidr,rp_oscidr,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_njdc3oc,rp_njdc3oc,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_txdc3oc,rp_txdc3oc,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_p2pincr2,rp_p2pincr2,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_p2p,rp_p2p,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_workstation,rp_three_workstation,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_voice,rp_three_voice,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_isolated,rp_three_isolated,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_p2p_cidr,rp_p2p_cidr,cid,region,clientfullname,networkdevice)
        devicetype = "sw01"
        add_host(devicetype,clientfullname,cid,region)
        add_CLI_networks_L3SW(CLI_networks,cid,region,clientfullname,networkdevice)
        text_to_dos()
        #add_monitoring_west(devicetype,clientfullname,cid,region,rp_snmp)
    elif "6" in n:
        clear()
        print("Configuring West 6. L2 SW (Just L2 switch no router)")

        #Inputs
        officesupernet = input("Provide office supernet with subnetmask via CIDR notation Ex. 10.214.20.0/22 \n")    

        #OfficeSupernet
        oscidr = officesupernet[-3:]
        subnetmask = cidr_to_netmask(officesupernet)[1]
        fourofficesupernet=officesupernet[:-3]
        threeofficesupernet = officesupernet[:-5]
         
        #Workstation
        officeworkstation = ipaddress.ip_address(fourofficesupernet) + 257
        workstation = str(officeworkstation)
        workstation = workstation[:-1] + "0"
        threenetworkstation = workstation[:-2]

        #Voice
        officevoice = ipaddress.ip_address(fourofficesupernet) + 513
        voice = str(officevoice)
        voice = voice[:-1] + "0"
        threenetvoice = voice[:-2]

        #Isolated
        officeisolated = ipaddress.ip_address(fourofficesupernet) + 771
        isolated = str(officeisolated)
        isolated = isolated[:-1] + "0"
        threenetisolated = isolated[:-2]


        #Keywords and replacement
        kw_cid = "@@cid@@"
        rp_cid = cid
        kw_region = "@@region@@"
        rp_region = region
        kw_snmp = "@@snmp@@"
        rp_snmp = snmp_psk_generated()[0]
        kw_psk = "@@psk@@"
        rp_psk = snmp_psk_generated()[1]
        kw_offsunetthree = "@@3osnet@@"
        rp_offsunetthree = threeofficesupernet    
        kw_oscidr = "@@oscidr@@"
        rp_oscidr = oscidr
        #Office supernet subnetmask
        kw_osunet_subnetmask="@@subnetmask@@"
        rp_osunet_subnetmask=subnetmask

        kw_three_workstation = "@@3osnetworkstation@@"
        rp_three_workstation =threenetworkstation
        kw_three_voice = "@@3osvoice@@"
        rp_three_voice =threenetvoice
        kw_three_isolated = "@@3isolatednet@@"
        rp_three_isolated =threenetisolated

        
        #Juniper switch01 24P and 48P
        
        networkdevice ="W_2x_dia_sw01_24P.txt"
        shutil.copy("/mnt/win_share/builds/config_files/West/2_2x_DIA/" + networkdevice,"/mnt/win_share/config_backup/" + clientfullname + "/" + cid +"/"+ cid +"_" + region + "_" + networkdevice)
        #Replace
        keywords_replace(kw_cid,rp_cid,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_region,rp_region,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_snmp,rp_snmp,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_psk,rp_psk,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_offsunetthree,rp_offsunetthree,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_oscidr,rp_oscidr,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_workstation,rp_three_workstation,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_voice,rp_three_voice,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_isolated,rp_three_isolated,cid,region,clientfullname,networkdevice)
        text_to_dos()
        
        networkdevice ="W_2x_dia_sw01_48P.txt"
        shutil.copy("/mnt/win_share/builds/config_files/West/2_2x_DIA/" + networkdevice,"/mnt/win_share/config_backup/" + clientfullname + "/" + cid +"/"+ cid +"_" + region + "_" + networkdevice)
        #Replace
        keywords_replace(kw_cid,rp_cid,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_region,rp_region,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_snmp,rp_snmp,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_psk,rp_psk,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_offsunetthree,rp_offsunetthree,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_oscidr,rp_oscidr,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_workstation,rp_three_workstation,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_voice,rp_three_voice,cid,region,clientfullname,networkdevice)
        keywords_replace(kw_three_isolated,rp_three_isolated,cid,region,clientfullname,networkdevice)
        devicetype = "sw01"
        add_host(devicetype,clientfullname,cid,region)
        text_to_dos()
        #add_monitoring_west(devicetype,clientfullname,cid,region,rp_snmp)
        #subprocess.Popen(["unix2dos", "/mnt/win_share/config_backup/",str(clientfullname),"/", str(cid), "/","*.txt"],stdout=subprocess.DEVNULL)

    else:
        print("Invalid input")












