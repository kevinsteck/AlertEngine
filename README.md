# Overview

The purpose of this code is to create a dynamic alerting system which allows groups consisting of multiple levels and escalation periods.  In its current state there are some logic errors (it sends to all groups regardless of escalation time on first action).  This will be fixed but this is very much in development.

# Features
* Stateful and nonstateful alerting.
* Ability to ack/suppress alerts.
* Alerting via multiple methods (email, sms, POST callbacks) 