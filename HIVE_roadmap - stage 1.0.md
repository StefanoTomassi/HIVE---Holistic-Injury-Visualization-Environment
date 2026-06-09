# HIVE – Holistic Injury Visualization Environment

## Overview

HIVE is a modular software environment for the post-processing and visualization of LS-DYNA simulation results.  
Its goal is to provide a structured and extensible framework to visualize raw LS-DYNA simulation outputs into clear plots and animations in an interactive web-based visualization.

HIVE is designed as a complete software platform composed of:

- a **backend**, responsible for data reading, metadata definition, case-specific computations, and generation of derived quantities;
- a **frontend**, responsible for graphical interaction, plot selection, multi-case comparison, and export of visual outputs.

The software relies **exclusively on Dynasaur** to read the binary LS-DYNA output files.  
In the current development stage, only **binout** is considered as output source.  
Dynasaur acts as the bridge between LS-DYNA raw data and HIVE, converting binary output and model-related information into structured data that can be processed by Python plotting libraries.

## Main objective

The main objective of HIVE is to simplify and standardize the analysis of LS-DYNA simulations for injury and safety-related applications.  
Instead of manually extracting signals, selecting parts, and producing figures for each simulation, the user should be able to:

1. provide the LS-DYNA simulation input and output files;
2. select the analysis case of interest;
3. access an interactive web page where the relevant plots and additional information are automatically generated;
4. Navigate the results and export the produced figures in high-quality formats such as SVG.

In this way, HIVE aims to reduce repetitive post-processing work and provide a consistent environment for both engineering analysis and scientific publication.

## Input philosophy

HIVE is built around a user-driven workflow.

For each simulation, the user manually provides a folder containing:

- the LS-DYNA keyword input cards;
- the `binout` output database;
- additional model-related files if needed, such as mesh and part definitions.

The LS-DYNA keyword cards are important because they define the simulation context and support the generation of metadata.  
This metadata is not intended to be fully generic, but rather **case-aware**.  
For example, a whiplash simulation should expose metadata and available quantities relevant to whiplash analysis, while quantities that are not meaningful for that case should not be proposed.

## Analysis philosophy

HIVE is organized around **fixed application cases**.  
Each case corresponds to a specific family of analyses and visualizations, for example:

- whiplash;
- airbag;
- energy balance.

Each case module should define:

- the relevant signals and entities to extract;
- the criteria to compute;
- the plots to generate;
- the additional information to display in the frontend.

This means that HIVE is not only a plotting tool.  
It is also intended to expose computed quantities, derived indicators, and contextual information directly in the web interface.

For example, in a whiplash module, the displayed outputs may include:

- spine curvature;
- strain of selected LS-DYNA parts;
- trajectories of the spine;
- trajectory of the head center of gravity;
- theta-based injury criteria;
- other case-specific injury metrics.

## Visualization goals

The visualization layer of HIVE should support both analysis and communication.

The frontend should allow the user to:

- select which simulations to compare;
- show multiple plots at the same time;
- inspect values interactively through hover actions;
- select specific parts for strain visualization;
- choose the type of plot to display;
- export figures in vector formats such as SVG.

Although the frontend is interactive, the plotting philosophy should remain oriented toward **state-of-the-art scientific visualization**.  
For this reason, the backend plot generation should rely primarily on Python libraries such as **Matplotlib** and **Seaborn**, which are well suited for publication-quality figure generation and SVG export.

## Software architecture

A possible high-level structure for HIVE is the following:

```text
HIVE/
├── core/
│   ├── classes.py
│   ├── read_ls_dyna_files.py
│   ├── metadata.py
│   ├── registry.py
│   ├── plot_manager.py
│   └── export.py
├── whiplash/
│   ├── module.py
│   ├── compute_injury_criteria.py
│   ├── generate_plot.py
│   ├── metadata.py
│   └── definitions.py
├── airbag/
│   ├── module.py
│   ├── compute_injury_criteria.py
│   ├── generate_plot.py
│   ├── metadata.py
│   └── definitions.py
├── energy_balance/
│   ├── module.py
│   ├── compute_energy_metrics.py
│   ├── generate_plot.py
│   ├── metadata.py
│   └── definitions.py
├── frontend/
│   ├── app/
│   ├── components/
│   ├── pages/
│   └── services/
└── main.py
```

## Role of the core

The `core` package should contain all the generic and reusable functionalities shared across the software.

Its responsibilities should include:

- handling simulation-level objects;
- interfacing with Dynasaur outputs;
- parsing keyword-card information needed for metadata definition;
- defining common visualization objects;
- managing plot styles and export options;
- providing abstract interfaces for future case modules.

The core should not contain logic that is specific to a single application case.  
Instead, it should provide the infrastructure that allows case modules to be added in a scalable way.

## Suggested class design

The classes you already defined are a very good starting point.  
They already separate simulation description, plotting style, animation settings, and visualization definitions.

A refined version could be:

### `SimulationData`
Stores all information required to describe a simulation instance.

Possible responsibility:
- simulation name;
- simulation type;
- paths to keyword input, mesh, part file, and `binout`;
- output directory;
- optional references to available criteria or computed results.

### `PlotStyle`
Stores the styling parameters used to make figures consistent and publication-ready.

Possible responsibility:
- typography;
- axes appearance;
- tick settings;
- line thickness;
- export settings for PDF/PS/SVG;
- DPI and general Matplotlib configuration.

### `AnimationStyle`
Stores settings related to animated or component-based visualization.

Possible responsibility:
- list of components to animate or display;
- configuration of animated entities in the frontend.

### `DataVisualizationDefinition`
Defines a plot or data view in a generic way.

Possible responsibility:
- plot name;
- module or case it belongs to;
- plot type;
- variable identifiers;
- x and y axes definitions.

## Additional classes to consider

To make the architecture more extensible, the following classes could also be introduced:

### `CaseModule`
An abstract base class defining the interface that every case-specific module must implement.

Possible methods:
- `load_metadata()`
- `available_plots()`
- `compute_criteria()`
- `build_visualizations()`

### `MetadataDefinition`
A class responsible for storing and validating the metadata relevant to a given simulation type.

This would help separate:
- raw extracted data;
- simulation metadata;
- case-specific display configuration.

### `PlotRequest`
A lightweight object representing what the user wants to visualize.

Possible fields:
- selected case;
- selected simulations;
- selected parts;
- selected plot types;
- export format.

## Case-module philosophy

Each case module should behave as an independent plug-in built on top of the core.

A module should define:
- what is relevant for the case;
- what data is available;
- what can be computed;
- what can be plotted;
- what should be shown in the web page.

This makes future extension easier, because adding a new case should mainly require:
1. creating a new module folder;
2. implementing the common case interface;
3. registering the new module in the core registry.

## Frontend philosophy

The frontend should act as an interactive analysis dashboard.

A possible workflow is:

1. the user uploads or selects one or more simulation folders;
2. the backend reads the LS-DYNA keyword cards and `binout` via Dynasaur;
3. HIVE identifies the selected analysis case;
4. the frontend exposes only the relevant plots and display options for that case;
5. the user compares simulations, selects parts, and inspects figures interactively;
6. the backend generates high-quality plots and allows export as SVG.

This architecture keeps the scientific logic in Python while using the web layer as an intuitive access point for exploration and comparison.

## Design principles

The development of HIVE should follow a few key principles:

- **modularity**, to support new analysis cases over time;
- **clarity**, to expose only meaningful quantities for each simulation type;
- **consistency**, to generate homogeneous plots and interfaces;
- **extensibility**, to make new modules easy to integrate;
- **publication quality**, to ensure that exported figures are immediately useful for reports and papers;
- **interactivity**, to improve the exploration of simulation results.

## Summary of the intended workflow

The intended HIVE workflow can be summarized as follows:

1. User selects one or more simulation folders.
2. HIVE reads LS-DYNA keyword cards and `binout` through Dynasaur.
3. Core utilities organize data and generate case-aware metadata.
4. The selected case module computes criteria and defines available visualizations.
5. The frontend displays interactive plots and additional simulation information.
6. The user compares cases, selects details of interest, and exports figures.

## Initial conclusion

HIVE should be developed as a modular LS-DYNA post-processing platform that combines:
- **Dynasaur for binary reading**,
- **Python for scientific processing and plotting**,
- **a web frontend for interactive exploration**.

Its architecture should separate generic infrastructure from case-specific knowledge, so that future modules can be added without changing the overall software design.