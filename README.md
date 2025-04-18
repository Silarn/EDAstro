A simple [E:D Market Connector][EDMC] plugin to automatically collect data for
EDAstro.com that cannot be sourced from major databases such as Spansh and EDDN.

### Sensitive Data
The EDAstro API requests certain potentially sensitive events: **CarrierStatus**
and **CarrierJumpRequest**. Since not everyone may want to submit this data,
these particular events are opt-in.

Note, however, that this plugin sanitizes data from these events and is limited to:
* Callsign
* Name
* ID
* Current / target system
* Access flags
* Fuel level

### Please Note
This plugin largely replicates the EDAstro functionality in [EDDiscovery]. You
***do not*** need this if you already report data via EDD. This is essentially
a lightweight alternative, or for those already submitting data via EDMC.

### Credit
This code is derived from the original [ATEL-EDMC] plugin with the IGAU
components stripped out. As this is no longer maintained and there is still a
community need to submit relevant data to EDAstro, I have revived that portion
of the plugin.

### Installation
Simply drop the [release archive] contents into the EDMC plugins directory. This
can by found within the EDMC settings incuding a button to open the directory.
The plugin will attempt to auto-update itself on launch if a new release is
detected.

[EDMC]: https://github.com/EDCD/EDMarketConnector
[EDDiscovery]: https://github.com/EDDiscovery/EDDiscovery
[ATEL-EDMC]: https://github.com/Intergalactic-Astronomical-Union/ATEL-EDMC
[release archive]: https://github.com/Silarn/EDAstro/releases/latest