# GenNotes

**GenNotes** and **Genevieve** are a pair of projects designed to empower individuals to understand putative diseases or traits reported for variants in a personal genome.

**Chat via IRC:** #gennotes on irc.freenode. If you're new to IRC, the easiest way to join is Freenode's webchat interface: http://webchat.freenode.net/?channels=gennotes

**Languages**: Python (Django), JavaScript, CSS, HTML

## Motivation

We’d like to empower understanding about claims of diseases or traits caused by variants in a personal genome, and comment upon these claims.

ClinVar a public domain resource that aggregates and reports assertions of clinical impact of genetic variants. While invaluable, these assertions can be flawed – this is especially apparent when evaluating assertions made for a personal genome. Coupling genome reports with consensus, structured note-taking helps re-evaluate assertions efficiently, and improves the quality of reports generated for future genomes.

To this end, we’d like to develop a series of related open source tools:
- **GenNotes**
  - A web server storing publicly shared and flexibly structured tags associated with genetic variants. These tags are structured as key/value tags, in the manner of Open Street Map. These can be arbitrary keys, but initially we'd like to focus on ClinVar and Genevieve tags.
- **Genevieve**
  - A client web app that can process individual genomes to find variants matching ClinVar positions. Using GenNotes, the client retrieves and reports the latest ClinVar and Genevieve tags for this variant list.

## Pre-sprint

We plan to have the following in place to support the sprint.
- GenNotes server (Django web app)
  - User accounts
  - Variant model, pre-populated with variants found in ClinVar
  - Key/value tag model
- Genevieve client (Django web app)
  - User accounts
  - genome file upload (VCF format)
  - process VCF to store in db variants matching ClinVar records ("variant report")

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
