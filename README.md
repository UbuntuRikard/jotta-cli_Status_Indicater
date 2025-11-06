# Jotta Status Indicator

A **minimal System Tray GUI for monitoring the status** of an external file synchronization client (specifically designed to check the output of the `jotta-cli status` command).

**jotta_status_indicator.py is not part of Jottacloud** it was created to provide an overview of whether jottad is running and what its current status is, which it achieves using the jotta_cli status command.

#### The status found here is interpreted and translated into an icon state:

* A green icon with a check mark that alternates between a normal check mark and an inverse check mark. This is done to show that monitoring is active and watching the status, thus preventing it from being just a static check mark display.
    
* There is also a white synchronization symbol, which indicates an active synchronization state.

* Then there is an icon with a red circle containing an exclamation mark (!). This indicates that something is wrong and that it is necessary to check what went wrong.

This can be done by opening the log file that Jotta itself continuously generates. You can also choose to view the actual active status, which you would normally see by running jotta_cli status.

#### In jotta_status_indicator, two menu items have been created:

* Actual Status: This executes the command and continuously displays the state: "jotta_cli status".

* Open Log File: This opens the standard log file for jottad in the default text editor so you can see what is wrong.

Thus, the jotta_status_indicator.py program is simply a user interface for the existing system, made easily accessible.

**jotta_status_indicator is intended for users who only use the CLI (Command Line Interface) interface for Jotta.**

#### Note/Addition:**

###### Please note: For the first minute after the computer starts, a warning that something is wrong may typically appear. This is because jottad must first connect to its server, and until it does, running jotta_cli status will show an error status. If it takes longer than a minute for the system to be ready and connected to the server, something may be wrong, and you can then choose to open the "Actual Status" menu to see what is happening.
Jotta_status_indicator checks the status every 5 seconds. Therefore, synchronization periods shorter than 5 seconds may not necessarily be visible live, but if synchronization is completed without issues, the status will still be green and thus correct.**
---

## 🛠️ Installation and Setup

**Se the INSTALL.md**
