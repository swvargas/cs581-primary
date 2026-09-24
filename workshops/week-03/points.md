# Point map — RMS

Every address your protocol server exposes. Six to twelve points.
This must match what a client actually reads from your service; the status probe compares them.

| Address | Name | Type | Units | Range | R/W | What it represents |
|---|---|---|---|---|---|---|
| 40001 | | holding | | | R | |
| 40002 | | holding | | | R | |
| 00001 | | coil | | 0/1 | R/W | |

## Process behaviour

Describe what moves and why. Values must not be static; the probe reads twice and compares.

## What this model does not represent

The simplification you chose, and what an analyst would wrongly conclude from it.
