# ansible-oracle-modules #

## Fork from oravirt/ansible-oracle-modules

This project is a fork from https://github.com/oravirt/ansible-oracle-modules made by @oravirt.

### Difference from @oravirt project ###

So far, I've :

1. fixed documentation generation (ansible-doc is now working),
1. fixed some errors in oracle_user module (thanks to @tekkamanendless),
1. created an oracle_directory module,
1. refactored oracle_tablespace module,
1. started to add tests for changed modules.

### What next ? ###

I'm planning to :

1. continue refactoring some modules to implements check mode, diff mode and return ddls executed (oracle-user, oracle-grants, ...),
1. transform this project in an ansible-galaxy collection to ease is reusability,
1. maybe add versions number for easier change tracking.

### Tests ###

Changes were tested with Ansible 2.8 and Python 3.

## Oracle modules for Ansible ##

Initial readme can be found here : https://github.com/oravirt/ansible-oracle-modules/blob/master/README.md. 

I'll describe only modules I refactored or created.

### Pre-requisite ###

The Python module `cx_Oracle` needs to be installed on the Ansible host. (`pip install cx_Oracle`)

### Created or refactored modules ###

#### oracle_directory ####

- This module manage Oracle directory objects.
- It can create, replace or drop directories.

#### oracle_tablespace ####

- This module manage Oracle tablespace objects.
- It can create, alter or drop tablespaces and datafiles.
- It supports permanent, undo and temporary tablespaces.
- It supports online/offline state and read only/read write state.
- It doesn't support defining default tablespace and other more specific actions.
- It supports check mode, diff mode and it returns DDL requests executed by the module.

### Unchanged modules ###

#### oracle_asmdg ####

pre-req: cx_Oracle

- Manages ASM diskgroup state. (absent/present)
- Takes a list of disks and makes sure those disks are part of the DG.
If the disk is removed from the disk it will be removed from the DG.
- Also manages attributes

**Note:**
- Supports redundancy levels, but does not yet handle specifying failuregroups

#### oracle_asmvol ####

- Manages ASM volumes. (absent/present)

#### oracle_awr ####

pre-req: cx_Oracle, datetime

- Manages AWR snapshot settings

#### oracle_datapatch ####

#### oracle_db ####

pre-rec: cx_Oracle

- Create/remove databases (cdb/non-cdb)
- Can be created by passing in a responsefile or just by using parameters

#### oracle_facts ####

pre-req: cx_Oracle

- Gathers facts about Oracle database

#### oracle_gi_facts ####

- Gathers facts about Grid Infrastructure cluster configuration

#### oracle_grants ####

pre-req: cx_Oracle

- Manages privileges for a user
- Grants/revokes privileges
- Handles roles/sys privileges properly. Does NOT yet handle object privs. They can be added but they are not considered while revoking privileges
- The grants can be added as a string (dba,'select any dictionary','create any table'), or in a list (ie.g for use with with_items)

#### oracle_job ####

pre-req: cx_Oracle, re

- Manages DBMS_SCHEDULER jobs

#### oracle_jobclass ####

pre-req: cx_Oracle

- Manages DBMS_SCHEDULER job classes

#### oracle_jobschedule ####

pre-req: cx_Oracle, re

- Manages DBMS_SCHEDULER job schedules

#### oracle_jobwindow ####

pre-req: cx_Oracle, datetime

- Manages DBMS_SCHEDULER windows

#### oracle_ldapuser ####

pre-req: cx_Oracle, ldap, re

- Syncronises users/role grants from LDAP/Active Directory to the database

#### oracle_opatch ####

#### oracle_parameter ####

pre-req: cx_Oracle

- Manages init parameters in the database (i.e alter system set parameter...)
- Also handles underscore parameters. That will require using mode=sysdba, to be able to read the X$ tables needed to verify the existence of the parameter.

**Note:**
When specifying sga-parameters the database requests memory based on granules which are variable in size depending on the size requested,
and that means the database may round the requested value to the nearest multiple of a granule.
e.g sga_max_size=1500M will be rounded up to 1504 (which is 94 granules of 16MB). That will cause the displayed value to be 1504M, which has
the effect that the next time the module is is run with a desired value of 1500M it will be changed again.
So that is something to consider when setting parameters that affects the SGA.

#### oracle_pdb ####

pre-req: cx_Oracle

- Manages pluggable databases in an Oracle container database
- Creates/deletes/opens/closes the pdb
- saves the state if you want it to. Default is yes
- Can place the datafiles in a separate location

#### oracle_privs ####

pre-req: cx_Oracle, re

- Manages system and object level grants
- Object level grant support wildcards, so now it is possible to grant access to all tables in a schema and maintain it automatically!

#### oracle_profile ####

#### oracle_redo ####

pre-rec: cx_Oracle

- Manage redo-groups and their size in RAC or single instance environments
- NOTE: For RAC environments, the database needs to be in ARCHIVELOG mode. This is not required for SI environments.

#### oracle_role ####

pre-req: cx_Oracle

- Manages roles in the database

#### oracle_rsrc_consgroup ####

pre-req: cx_Oracle, re

- Manages resource manager consumer groups including its mappings and grants

#### oracle_services ####

pre-req: cx_Oracle (if GI is not running)

- Manages services in an Oracle database (RAC/Single instance)

**Note:**
At the moment, Idempotence only applies to the state (present,absent,started, stopped). No other options are considered.

#### oracle_sql ####

pre-req: cx_Oracle

- 2 modes: sql or script
- Executes arbitrary sql or runs a script

**Note:**
Should be considered as experimental, or an alpha-release

#### oracle_stats_prefs ####

pre-req: cx_Oracle

- Managing DBMS_STATS global preferences

#### oracle_user ####

pre-req: cx_Oracle

- Creates & drops a user.
- Grants privileges only (can not remove them with oracle_user, use oracle_grants for that)
