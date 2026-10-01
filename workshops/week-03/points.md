# Point map — RMS

Every address your protocol server exposes. Six to twelve points.
This must match what a client actually reads from your service; the status probe compares them.

| Address | Name | Type | Units | Range | R/W | What it represents |
|---|---|---|---|---|---|---|
| 40001 | area_radiation | holding | uSv/h x 100 | 0-10000 | R | Simulated ambient radiation level |
| 40002 | count_rate | holding | CPS | 0-65535 | R | Detector counts derived from radiation |
| 40003 | detector_temperature | holding | deg C x 10 | 0-1000 | R | Slowly varying detector temperature |
| 40004 | alarm_threshold | holding | uSv/h x 100 | 1-10000 | R/W | High-radiation alarm threshold |
| 40005 | detector_health | holding | percent | 0-100 | R | Simulated detector health |
| 40006 | sample_counter | holding | samples | 0-65535 | R | Increments once per simulation update |
| 00001 | alarm_acknowledge | coil | boolean | 0/1 | R/W | Operator alarm acknowledgement |
| 00002 | high_radiation_alarm | coil | boolean | 0/1 | R | Radiation exceeds the configured threshold |

Client offsets are zero-based: 40001 is holding-register offset 0, and 00001 is
coil offset 0. The Modbus device ID is 1. Integer scaling is used because these
points are represented by 16-bit registers.

## Process behaviour

The process updates once per second. Radiation combines a baseline, slow sine-wave
variation, and bounded random noise. Count rate follows radiation with additional
noise. Detector temperature changes on a slower period, detector health remains in
a bounded operating range, and the sample counter increments on every update. The
high-radiation coil follows the comparison between radiation and the writable alarm
threshold.

## What this model does not represent

This is a training simulation, not a calibrated radiation detector. It does not model
detector dead time, isotope spectra, shielding, spatial distribution, calibration
drift, communication latency, or equipment failure. An analyst must not interpret
its values as physical measurements or assume that a healthy percentage proves the
integrity of a real detector.
