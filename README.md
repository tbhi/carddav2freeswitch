# CardDAV-to-FreeSWITCH import

This script reads all contacts from a CardDAV addressbook and puts them into memcached so FreeSWITCH's cidlookup app
can read them

If there's already an entry in memcached for a specific number, this script updates the number with the new name.

Forked from https://github.com/citronalco/carddav2asterisk.

### Requirements
* Python 3
* pipenv

### Usage
#### Configuration

See https://freeswitch.org/confluence/display/FREESWITCH/mod_cidlookup
