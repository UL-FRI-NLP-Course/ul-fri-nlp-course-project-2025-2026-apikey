# Domain-Specific Fitness NLP Assistant Using Retrieval-Augmented Generation


Domen Pahole, Luka Rizman, Nina Trivić


# NLP Course Project Repository

This repository is organized for Submission 1 of the university Natural Language Processing course. It is structured as a clean workspace for project selection, dataset documentation, and initial corpus analysis.

## Project Scope

The repository currently supports the first project milestone:

- project selection and framing
- dataset discovery and documentation
- simple corpus analysis on small local samples
- reproducible documentation for the first milestone
- clean separation between report and data

Replace the placeholder dataset entries in [data/README.md](data/README.md) with the exact datasets chosen by your team.

## Repository Structure

```text
.
├── data/
│   ├── raw/
│   ├── samples/
│   ├── processed/
│   └── README.md
├── report/
│   ├── fig/
│   ├── report.tex
│   ├── report.pdf
│   ├── report.bib
│   └── ds_report.cls
├── README.md
└── LICENSE
```

## Dataset Links

Dataset documentation lives in [data/README.md](data/README.md). That file should be treated as the authoritative source for:

- dataset names
- official links
- licensing constraints
- motivation for dataset selection
- notes on whether only metadata or small samples are stored locally

## Reproducibility

1. Document the selected datasets in [data/README.md](data/README.md).
2. Store only tiny sample files in `data/samples/`.
3. Record any manual download or preprocessing steps in the report and data documentation.

## Corpus Analysis Workflow

The initial analysis pipeline is:

1. document candidate datasets in [data/README.md](data/README.md)
2. place a small representative sample in `data/samples/`
3. compute and summarize corpus statistics
4. report findings in the written submission

## Expected Pipeline

- raw data references and metadata in `data/raw/`
- lightweight analysis samples in `data/samples/`
- cleaned intermediate outputs in `data/processed/`
- narrative reporting in `report/`