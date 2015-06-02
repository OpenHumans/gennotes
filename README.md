# GenNotes

**GenNotes** and **Genevieve** are a pair of projects designed to empower
individuals to understand putative effects reported for variants in an
individual genome. We're planning to work on these during the [Mozilla Science
Lab Global Sprint 2015](https://www.mozillascience.org/global-sprint-2015), on
June 4th and 5th.

**Chat via IRC:** #gennotes on irc.freenode. If you're new to IRC, the easiest
way to join is Freenode's webchat interface:
http://webchat.freenode.net/?channels=gennotes

**Languages**: Python (Django), JavaScript, CSS, HTML

## Local development set-up

We've set up a copy of GenNotes running on Heroku at
[gennotes.herokuapp.com](http://gennotes.herokuapp.com/) (NOT REMOTELY STABLE).
While users can run their own copy of
[Genevieve](https://github.com/PersonalGenomesOrg/genevieve), the intention
is to have a single GenNotes service that every copy of Genevieve talks to.
The instructions are *only* intended to assist developers interested in
contributing to the centrally-run website's features.

* **Use pip and virtualenv. In the virtualenv install required packages with:
`pip install -r requirements.txt`**
  * If pip and virtualenv are new to you, this repo may not be the best place
to start learning! Maybe you'd be interested in contributing to [Genevieve](https://github.com/PersonalGenomesOrg/genevieve)?
* **Set up PostgreSQL**
  * Ubuntu/Debian
    * For working with PostgreSQL: `sudo apt-get install libpq-dev python-dev`
    * Install PostgreSQL: `sudo apt-get install postgresql postgresql-contrib`
    * Become the postgres user: `sudo su - postgres`.
    * [as postgres] Create your databasae, e.g.: `createdb mydb`
    * [as postgres] Create your database user, e.g.: `createuser -P myuser`. Remember the password used, you'll need it in your configuration later!
    * [as postgres] Log in to PostgreSQL: `psql mydb`
    * [as postgres, in psql] Grant user privileges, e.g.: `GRANT ALL PRIVILEGES ON DATABASE mydb TO myuser;`
    * [as postgres, in psql] Add HStore extension to this database: `CREATE EXTENSION IF NOT EXISTS "hstore";`
    * Use `\q` to quit psql, and `exit` to log off as the postgres user.
  * *OSX instructions (Homebrew?) invited!*
* **Copy `env.example` to `.env`** (note the leading dot!)
  * Set your `SECRET_KEY` with a random string.
  * Set the `DATABASE_URL` using appropriate PostgreSQL database name, user, and password.
  * Set `PSQL_USER_IS_SUPERUSER = "False"`. (If "True" we can automatically install the hstore extension duing the first migration, but you've already done this manually.)
  * The easiest mail set-up is probably to set `EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"`. Emails "sent" by the site will show up in console output.
* **Initialize the database:** `python manage.py migrate`
* **Run the site:** `python manage.py runserver`
* You can now load GenNotes in your web browser by visiting `http://localhost:8000/`.
* You can also interact directly with your site via shell_plus using `python manage.py shell_plus`

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
  - :white_check_mark: Variant model, pre-populated with variants found in ClinVar
  - :white_check_mark: Key/value tag model
  - :white_check_mark: Django-reversion history for elements and tags.
- [Genevieve client](https://github.com/PersonalGenomesOrg/genevieve)
  - :white_check_mark: Django web app
  - :white_check_mark: User accounts
  - :white_check_mark: genome file upload (VCF format)
  - :white_check_mark: process VCF to store in db variants matching ClinVar records ("variant report")

## Sprint goals
- **Add Clinvar:** On the GenNotes server, import ClinVar key/value tags.
  - (tagging variant) "clinvar_accession": [clinvar accession]
  - (tagging clinvar-accession) "clinvar_significance": [Uncertain significance/not provided/Benign/Likely benign/Likely pathogenic/Pathogenic/drug response/histocompatibility/other]
  - (tagging clinvar-accession) "clinvar_disease": [disease name]
- **Programmatic tag submission:** Specify the method (widget/API) for client apps to update or submit new tags
- **Display GenNotes data in Genevieve:** make Genevieve client variant report with an AJAX GenNotes query, displaying returned ClinVar & Genevieve tag data
- **Implement tag submission:** Implement tag submission on Genevieve client to add/update following tags
  - (tagging clinvar-accession) "genevieve_inheritance": [dominant/recessive/additive/-] (default: -)
  - (tagging clinvar-accession) "genevieve_evidence": [well-established/reported/disputed/disproven] (default: reported)
  - (tagging clinvar-accession) "genevieve_notes": free text field for explaining rationale for current genevieve evaluation

## Secondary/stretch projects
- Parse and import ExAC key/value tags for variant positions
- Parse and import dbSNP key/value tags for variant positions
