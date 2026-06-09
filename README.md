# carbo-verdant
Machine learning and remote sensing pipeline for modeling forest carbon sequestration.

## Overview

A minimalist pipeline to rapidly estimate carbon sequestration and assess landcover management impact.

Proof-of-concept will compare a small agroforestry holding and compare the estimated carbon sequestration to it's surrounding environment.

## How it works

1. User defines a boundary and a timeframe
2. Pipeline gets satellite imagery, computes NDVI for the area, estimates biomass and carbon sequestration.
3. Outputs are visualized in UI: maps, trends, ...

## Roadmap

### POC

- Get satellite data
- Compute features
- Plots of interest

### SLC

- Develop API & UI
- Make it cloud-based

### TODO

- Validate Pydantic models
    - Add a area limit to input (50 ha)
    - Add a limit to timeseries (scope defined by S2)
- Store downloaded image per ID to avoid step rerun

## Problematics

- How to estimate biomass from the different forest strata ?  
    - Look into EVI
- How to estimate biomass w/o groundtruth ?
    - Look at trends
    - Build a similarity embedding


