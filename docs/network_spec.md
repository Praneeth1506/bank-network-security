# BankNet network spec (CN Lab CA2, Problem 8)

Single source of truth for the companion app. Person A owns the backend
(vlsm.py, main.py, config generator, seed script). Person B owns acl.py and
the React frontend. Do not edit acl.py or frontend/ unless asked.

## 1. Addressing (block 10.80.0.0/24, sized for 100% growth + 1 gateway)

| VLAN | Name    | Hosts | Network      | Prefix | Mask            | Wildcard | Gateway    | First      | Last       | Broadcast  | Usable |
|------|---------|-------|--------------|--------|-----------------|----------|------------|------------|------------|------------|--------|
| 10   | KIOSK   | 10    | 10.80.0.0    | 27     | 255.255.255.224 | 0.0.0.31 | 10.80.0.1  | 10.80.0.1  | 10.80.0.30 | 10.80.0.31 | 30     |
| 20   | TELLER  | 8     | 10.80.0.32   | 27     | 255.255.255.224 | 0.0.0.31 | 10.80.0.33 | 10.80.0.33 | 10.80.0.62 | 10.80.0.63 | 30     |
| 30   | MANAGER | 2     | 10.80.0.64   | 29     | 255.255.255.248 | 0.0.0.7  | 10.80.0.65 | 10.80.0.65 | 10.80.0.70 | 10.80.0.71 | 6      |
| 40   | SERVER  | 1     | 10.80.0.72   | 29     | 255.255.255.248 | 0.0.0.7  | 10.80.0.73 | 10.80.0.73 | 10.80.0.78 | 10.80.0.79 | 6      |
| 99   | MGMT    | 2     | 10.80.0.80   | 29     | 255.255.255.248 | 0.0.0.7  | 10.80.0.81 | 10.80.0.81 | 10.80.0.86 | 10.80.0.87 | 6      |
| 999  | PARKING | 0     | (no IP; native VLAN on trunks and VLAN for unused ports)                                                       |

Reserved for growth: 10.80.0.88/29, 10.80.0.96/27, 10.80.0.128/25.

Hosts: KIOSK1-10 DHCP (pool .6-.30, .1-.5 excluded); TELLER1-8 10.80.0.34-.41;
MGR1 10.80.0.66, MGR2 10.80.0.67; SRV1 10.80.0.74; SW1 SVI 10.80.0.82; SW2 SVI 10.80.0.83.

## 2. Port map

| Device | Ports                    | Connects to         | Mode / VLAN                          |
|--------|--------------------------|---------------------|--------------------------------------|
| R1     | G0/0                     | SW1 Gi0/1           | 802.1Q trunk, subinterfaces          |
| R1     | G0/1, G0/2               | none                | shutdown                             |
| SW1    | Fa0/1-10                 | KIOSK1-10           | access 10, portfast, bpduguard       |
| SW1    | Fa0/11                   | SRV1                | access 40, portfast                  |
| SW1    | Fa0/23-24                | SW2 Fa0/23-24       | trunk, Po1 LACP active               |
| SW1    | Fa0/12-22, Gi0/2         | none                | access 999, shutdown                 |
| SW2    | Fa0/1-8                  | TELLER1-8           | access 20, port security, portfast   |
| SW2    | Fa0/9-10                 | MGR1-2              | access 30, portfast                  |
| SW2    | Fa0/23-24                | SW1 Fa0/23-24       | trunk, Po1 LACP active               |
| SW2    | Fa0/11-22, Gi0/1-2       | none                | access 999, shutdown                 |

Trunks: native VLAN 999, allowed 10,20,30,40,99, nonegotiate.

## 3. Reference configs (generator output must match these line for line)

### SW1
```
enable
configure terminal
hostname SW1
no ip domain-lookup
enable secret Bank@Enable26
service password-encryption
banner motd #Authorized access only#
username admin privilege 15 secret Bank@Admin26
ip domain-name bank.local
crypto key generate rsa general-keys modulus 1024
ip ssh version 2
!
vlan 10
 name KIOSK
vlan 20
 name TELLER
vlan 30
 name MANAGER
vlan 40
 name SERVER
vlan 99
 name MGMT
vlan 999
 name PARKING
!
interface GigabitEthernet0/1
 description Trunk to R1 G0/0
 switchport mode trunk
 switchport trunk native vlan 999
 switchport trunk allowed vlan 10,20,30,40,99
 switchport nonegotiate
!
interface range FastEthernet0/23 - 24
 description EtherChannel to SW2
 switchport mode trunk
 switchport trunk native vlan 999
 switchport trunk allowed vlan 10,20,30,40,99
 channel-group 1 mode active
interface Port-channel1
 switchport mode trunk
 switchport trunk native vlan 999
 switchport trunk allowed vlan 10,20,30,40,99
 switchport nonegotiate
!
interface range FastEthernet0/1 - 10
 description KIOSK
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
 spanning-tree bpduguard enable
interface FastEthernet0/11
 description SRV1
 switchport mode access
 switchport access vlan 40
 spanning-tree portfast
!
interface range FastEthernet0/12 - 22
 description UNUSED
 switchport mode access
 switchport access vlan 999
 shutdown
interface GigabitEthernet0/2
 description UNUSED
 switchport mode access
 switchport access vlan 999
 shutdown
!
interface Vlan1
 shutdown
interface Vlan99
 ip address 10.80.0.82 255.255.255.248
 no shutdown
ip default-gateway 10.80.0.81
!
access-list 10 permit 10.80.0.64 0.0.0.7
line vty 0 15
 access-class 10 in
 transport input ssh
 login local
 exec-timeout 5 0
line console 0
 password Bank@Con26
 login
end
copy running-config startup-config
```

### SW2
```
enable
configure terminal
hostname SW2
no ip domain-lookup
enable secret Bank@Enable26
service password-encryption
banner motd #Authorized access only#
username admin privilege 15 secret Bank@Admin26
ip domain-name bank.local
crypto key generate rsa general-keys modulus 1024
ip ssh version 2
!
vlan 10
 name KIOSK
vlan 20
 name TELLER
vlan 30
 name MANAGER
vlan 40
 name SERVER
vlan 99
 name MGMT
vlan 999
 name PARKING
!
interface range FastEthernet0/23 - 24
 description EtherChannel to SW1
 switchport mode trunk
 switchport trunk native vlan 999
 switchport trunk allowed vlan 10,20,30,40,99
 channel-group 1 mode active
interface Port-channel1
 switchport mode trunk
 switchport trunk native vlan 999
 switchport trunk allowed vlan 10,20,30,40,99
 switchport nonegotiate
!
interface range FastEthernet0/1 - 8
 description TELLER
 switchport mode access
 switchport access vlan 20
 switchport port-security
 switchport port-security maximum 1
 switchport port-security mac-address sticky
 switchport port-security violation shutdown
 spanning-tree portfast
!
interface range FastEthernet0/9 - 10
 description MANAGER
 switchport mode access
 switchport access vlan 30
 spanning-tree portfast
!
interface range FastEthernet0/11 - 22
 description UNUSED
 switchport mode access
 switchport access vlan 999
 shutdown
interface range GigabitEthernet0/1 - 2
 description UNUSED
 switchport mode access
 switchport access vlan 999
 shutdown
!
interface Vlan1
 shutdown
interface Vlan99
 ip address 10.80.0.83 255.255.255.248
 no shutdown
ip default-gateway 10.80.0.81
!
access-list 10 permit 10.80.0.64 0.0.0.7
line vty 0 15
 access-class 10 in
 transport input ssh
 login local
 exec-timeout 5 0
line console 0
 password Bank@Con26
 login
end
copy running-config startup-config
```

### R1
```
enable
configure terminal
hostname R1
no ip domain-lookup
enable secret Bank@Enable26
service password-encryption
banner motd #Authorized access only#
username admin privilege 15 secret Bank@Admin26
ip domain-name bank.local
crypto key generate rsa general-keys modulus 1024
ip ssh version 2
ip ssh time-out 60
ip ssh authentication-retries 3
!
interface GigabitEthernet0/0
 description Trunk to SW1 G0/1
 no ip address
 no shutdown
interface GigabitEthernet0/0.10
 description KIOSK
 encapsulation dot1Q 10
 ip address 10.80.0.1 255.255.255.224
interface GigabitEthernet0/0.20
 description TELLER
 encapsulation dot1Q 20
 ip address 10.80.0.33 255.255.255.224
interface GigabitEthernet0/0.30
 description MANAGER
 encapsulation dot1Q 30
 ip address 10.80.0.65 255.255.255.248
interface GigabitEthernet0/0.40
 description SERVER
 encapsulation dot1Q 40
 ip address 10.80.0.73 255.255.255.248
interface GigabitEthernet0/0.99
 description MGMT
 encapsulation dot1Q 99
 ip address 10.80.0.81 255.255.255.248
interface GigabitEthernet0/1
 shutdown
interface GigabitEthernet0/2
 shutdown
!
ip dhcp excluded-address 10.80.0.1 10.80.0.5
ip dhcp pool KIOSK
 network 10.80.0.0 255.255.255.224
 default-router 10.80.0.1
!
ip access-list extended KIOSK_IN
 permit udp any eq 68 any eq 67
 permit tcp 10.80.0.0 0.0.0.31 host 10.80.0.74 eq 80
 permit tcp 10.80.0.0 0.0.0.31 host 10.80.0.74 eq 443
 permit tcp 10.80.0.0 0.0.0.31 10.80.0.64 0.0.0.7 established
 permit icmp 10.80.0.0 0.0.0.31 10.80.0.64 0.0.0.7 echo-reply
 deny ip any any
!
ip access-list extended TELLER_IN
 permit tcp 10.80.0.32 0.0.0.31 host 10.80.0.74 eq 80
 permit tcp 10.80.0.32 0.0.0.31 host 10.80.0.74 eq 443
 permit tcp 10.80.0.32 0.0.0.31 host 10.80.0.74 eq 21
 permit tcp 10.80.0.32 0.0.0.31 host 10.80.0.74 eq 20
 permit tcp 10.80.0.32 0.0.0.31 10.80.0.64 0.0.0.7 established
 permit icmp 10.80.0.32 0.0.0.31 10.80.0.64 0.0.0.7 echo-reply
 deny ip 10.80.0.32 0.0.0.31 10.80.0.0 0.0.0.31
 deny ip 10.80.0.32 0.0.0.31 10.80.0.64 0.0.0.7
 deny ip any any
!
interface GigabitEthernet0/0.10
 ip access-group KIOSK_IN in
interface GigabitEthernet0/0.20
 ip access-group TELLER_IN in
!
access-list 10 permit 10.80.0.64 0.0.0.7
line vty 0 15
 access-class 10 in
 transport input ssh
 login local
 exec-timeout 5 0
line console 0
 password Bank@Con26
 login
 logging synchronous
end
copy running-config startup-config
```

## 4. Test table (seed data, 18 rows)

| #  | Source       | Destination        | Test                                     | Expected |
|----|--------------|--------------------|------------------------------------------|----------|
| 1  | KIOSK1       | R1                 | ipconfig (DHCP lease)                    | Allowed  |
| 2  | KIOSK1       | SRV1               | Browser http://10.80.0.74                | Allowed  |
| 3  | KIOSK1       | SRV1               | Browser https://10.80.0.74               | Allowed  |
| 4  | KIOSK1       | SRV1               | ping 10.80.0.74                          | Blocked  |
| 5  | KIOSK1       | SRV1               | ftp 10.80.0.74                           | Blocked  |
| 6  | KIOSK1       | TELLER1            | ping 10.80.0.34                          | Blocked  |
| 7  | KIOSK1       | MGR1               | ping 10.80.0.66                          | Blocked  |
| 8  | TELLER1      | SRV1               | Browser http and https                   | Allowed  |
| 9  | TELLER1      | SRV1               | ftp 10.80.0.74, login teller, put/get    | Allowed  |
| 10 | TELLER1      | SRV1               | ping 10.80.0.74                          | Blocked  |
| 11 | TELLER1      | KIOSK1             | ping                                     | Blocked  |
| 12 | TELLER1      | MGR1               | ping 10.80.0.66                          | Blocked  |
| 13 | TELLER1      | R1                 | ssh -l admin 10.80.0.33                  | Blocked  |
| 14 | MGR1         | KIOSK1, TELLER1, SRV1 | ping                                  | Allowed  |
| 15 | MGR1         | SRV1               | Browser and FTP (manager account)        | Allowed  |
| 16 | MGR1         | R1, SW1, SW2       | ssh -l admin 10.80.0.65 / .82 / .83      | Allowed  |
| 17 | MGR1         | R1                 | telnet 10.80.0.65                        | Blocked  |
| 18 | ROGUE laptop | SW2 Fa0/3          | ping 10.80.0.33 (port security)          | Blocked  |

## 5. API contract agreed with Person B (frontend)

- GET  /api/config            -> {"devices": ["R1", "SW1", "SW2"]}
- GET  /api/config/{device}   -> {"device": "R1", "config": "<full text>"}; 404 for unknown device; device name case-insensitive
- GET  /api/config/{device}.txt -> same config as text/plain (download)
- Existing: POST /api/plan, POST /api/acl/check, GET/POST /api/tests, PATCH /api/tests/{id}, GET /api/tests/export.csv
