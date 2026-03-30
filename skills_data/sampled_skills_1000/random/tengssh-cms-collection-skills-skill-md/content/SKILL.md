--- 
name: Computational Materials Science Guidelines
description: Create, run, and analyze simulations. Manage data and utilize computing resources.
---
# Computational Materials Science Guidelines

## Overview

Computational Materials Science (CMS) is an interdisciplinary field that involves **defining problems** through the creation or selection of models for material systems of interest, **formulating system representations** (from atoms to continuum), **selecting methodologies/algorithms** (e.g., DFT, MD, Phase-field, or FEM) to solve problems, and **implementing models** on various computing systems. 

Typical CMS activities include **preparing inputs**, **managing and analyzing outputs**, **interpreting results**, **accelerating discoveries**, and **optimizing specific targets or processes** as needed.

## Capabilities
- **Plan**: literature, data, tools
- **Run**: select models/programs, prepare inputs, run simulations
- **Analyze**: monitor workflows, analyze outputs

## How to use
1. **Input data**: provide simulation inputs based on the selected models/programs
2. **Analysis**: perform analyses for specific scales
3. **Reproducibility**: reuse predefined workflows or define a new one if needed
4. **Publication**: collect output data and use paper template to draft a report

## Input format
### Atomistic scale
- Structures: `xyz`, `cif`, `pdb`, `POSCAR`, `data.in`
- Parameters: `run.in`, `INCAR`, `inp`, `POTCAR`
### Mesoscale
- Structures & Parameters: `opi`, `parameters.in`, `txt`
### Macroscale
- Structures & Parameters: `inp`, `mph`

## Output Format
- Main Outputs: `log`, `out`, `xml`, `OUTCAR` (energy, forces, stress tensors)
- Trajectories: `dump`, `xtc` (structural evolution)
- Electronic Distribution: `WAVECAR`, `CHGCAR`, `cube` (wavefunctions and charge density)
- Visualization in proper formats

## Example usage
"Run an EOF simulation on the perovskite KNbO3"

"List candidates of dielectric materials for TFET NVM"

"Identify the most efficient catalysts and  visualize the HER process at the atomic scale"

## Scripts
- `rag.py`: query contents using RAG
- `run_simulations.py`: main engines for running simulations
- `analysis.py`: analyze output data to provide insights

## Best practices
1. Always cite sources when collecting information and data
2. Use workflow management tools to handle environment, packages, data provenance and errors
3. Decide which operations to perform based on specific scales and applications
4. Consider a broader context for analysis, even when the simulation was performed at a certain scale
5. Include computing resource usage and runtime in the final report

## Limitations
- Require accurate materials data and correct model selection
- Many-body and relativistic effects may be crucial
- Some problems may be unsolvable on classical computers
