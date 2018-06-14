There are three interfaces:
 - telemetry
 - control
 - hardware

The idea is that the brain (which links all three) will be device independent
and so able to be run easily inside a simulator.



CURRENT THOUGHTS:
 - How to send things other than log messages through telemetry?
 - Where should the hardware abstraction layer lie?
