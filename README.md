# GenNotes

**GenNotes** and **Genevieve** are a pair of projects designed to empower individuals to understand putative effects reported for variants in an individual genome. We're planning to work on these during the [Mozilla Science Lab Global Sprint 2015](https://www.mozillascience.org/global-sprint-2015), on June 4th and 5th.

**Chat via IRC:** #gennotes on irc.freenode. If you're new to IRC, the easiest way to join is Freenode's webchat interface: http://webchat.freenode.net/?channels=gennotes

**Languages**: Python (Django), JavaScript, CSS, HTML

## Motivation

GenNotes and Genevieve are about accessing and improving genomic knowledge. We believe access and discussion of knowledge is a right and necessity for informed citizenry in the age of genomics. We want to facilitate access to published claims regarding the effects of variants in an individual genome, and enable discussion and consensus understanding of these claims.

We’d like to start by building understanding around ClinVar, a public domain resource that aggregates and reports assertions of clinical impact of genetic variants. While invaluable, these assertions can be flawed – this is especially apparent when evaluating assertions made for an individual genome. Coupling "genome reports" and "consensus, structured note-taking" helps evaluate assertions efficiently, and improves the quality of reports generated for future genomes.

To this end, we’d like to develop a set of related open source tools:
- **GenNotes**
  - A web server storing publicly shared and flexibly structured tags associated with genetic variants. These tags are structured as key/value tags, in the manner of Open Street Map. These can be arbitrary keys, but initially we'd like to focus on ClinVar and Genevieve tags.
- **Genevieve**
  - A client web app that can process individual genomes to find variants matching ClinVar positions. Using GenNotes, the client retrieves and reports the latest ClinVar and Genevieve tags for this variant list.
- **Connect these**
  - We want to enable Genevieve users to submit and edit structured notes to the GenNotes server regarding ClinVar assertions. We envision the associated GenNotes accounts to be open to all, and for contributors to Genevieve notes to agree to a CC0 public dedication for their edits.

### Not for clinical use!

The tools that we create for this project may involve claims related to health and disease, but primary literature is research: reports may be contradicted or challenged by later findings. Edits may come from any source and are not vetted. None of the resources produced in this project are for medical use and they should not be used as a substitute for professional medical care or advice. Users seeking information about a personal genetic disease, syndrome, or condition should consult with a qualified healthcare professional.

## Pre-sprint

We plan to have the following in place to support the sprint.
- GenNotes server (this repository)
  - :white_check_mark: Django web app
  - :white_check_mark: User accounts
  - :white_medium_square: Variant model, pre-populated with variants found in ClinVar
  - :white_medium_square: Key/value tag model
- [Genevieve client](https://github.com/PersonalGenomesOrg/genevieve)
  - :white_check_mark: Django web app
  - :white_check_mark: User accounts
  - :white_medium_square: genome file upload (VCF format)
  - :white_medium_square: process VCF to store in db variants matching ClinVar records ("variant report")

## Sprint goals
- **Add Clinvar:** On the GenNotes server, import ClinVar key/value tags.
  - (tagging variant) "clinvar-accession": [clinvar accession]
  - (tagging clinvar-accession) "clinvar-significance": [Uncertain significance/not provided/Benign/Likely benign/Likely pathogenic/Pathogenic/drug response/histocompatibility/other]
  - (tagging clinvar-accession) "clinvar-disease": [disease name]
- **Programmatic tag submission:** Specify the method (widget/API) for client apps to update or submit new tags
- **Display GenNotes data in Genevieve:** make Genevieve client variant report with an AJAX GenNotes query, displaying returned ClinVar & Genevieve tag data
- **Implement tag submission:** Implement tag submission on Genevieve client to add/update following tags
  - (tagging clinvar-accession) "genevieve-inheritance": [dominant/recessive/additive/-] (default: -)
  - (tagging clinvar-accession) "genevieve-evidence": [well-established/reported/disputed/disproven] (default: reported)
  - (tagging clinvar-accession) "genevieve-notes": free text field for explaining rationale for current genevieve evaluation

## Secondary/stretch projects
- Parse and import ExAC key/value tags for variant positions
- Parse and import dbSNP key/value tags for variant positions
