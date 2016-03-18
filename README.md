# GenNotes

[![Join the chat at https://gitter.im/PersonalGenomesOrg/gennotes](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/PersonalGenomesOrg/gennotes?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

**GenNotes** and **[Genevieve](https://github.com/PersonalGenomesOrg/genevieve)** are a pair of projects designed to empower
individuals to understand putative effects reported for variants in an
individual genome. We worked on these during the [Mozilla Science
Lab Global Sprint 2015](https://www.mozillascience.org/global-sprint-2015), and
are continuing work on the project.

**Chat via IRC or gitter:**
* #gennotes on irc.freenode. If you're new to IRC, the easiest
way to join is Freenode's webchat interface:
http://webchat.freenode.net/?channels=gennotes
* or, use your GitHub account to start a Gitter account and chat in our Gitter
room: https://gitter.im/PersonalGenomesOrg/gennotes
* These two rooms are synced by the GennoteGitterBot.

**Languages**: Python (Django), JavaScript, CSS, HTML

## Motivation

GenNotes and Genevieve are about accessing and improving genomic knowledge. We believe access and discussion of knowledge is a right and necessity for informed citizenry in the age of genomics. We want to facilitate access to published claims regarding the effects of variants in an individual genome, and enable discussion and consensus understanding of these claims.

We’d like to start by building understanding around ClinVar, a public domain resource that aggregates and reports assertions of clinical impact of genetic variants. While invaluable, these assertions can be flawed – this is especially apparent when evaluating assertions made for an individual genome. Coupling "genome reports" and "consensus, structured note-taking" helps evaluate assertions efficiently, and improves the quality of reports generated for future genomes.

To this end, we’re developing a set of related open source tools:
- **GenNotes**
  - A web server storing publicly shared and flexibly structured tags associated with genetic variants. These tags are structured as key/value tags, in the manner of Open Street Map. These can be arbitrary keys, but initially we'd like to focus on ClinVar and Genevieve tags.
- **Genevieve**
  - A client web app that can process individual genomes to find variants matching ClinVar positions. Using GenNotes, the client can retrieves and reports the latest ClinVar and Genevieve tags for this variant list. Genevieve users can then create and edit structured notes about ClinVar assertions. These notes are shared as a consensus understanding: they are stored by the GenNotes server and become visible and editable for all Genevieve users.

### Not for clinical use!

The tools that we create for this project may involve claims related to health and disease, but primary literature is research: reports may be contradicted or challenged by later findings. Edits may come from any source and are not vetted. None of the resources produced in this project are for medical use and they should not be used as a substitute for professional medical care or advice. Users seeking information about a personal genetic disease, syndrome, or condition should consult with a qualified healthcare professional.

## TODO List

The basic structure for these projects is now complete, but it's a "bare bones" implementation. There remain numerous issues and improvements: see [GenNotes issues](https://github.com/PersonalGenomesOrg/gennotes/issues) and [Genevieve issues](https://github.com/PersonalGenomesOrg/genevieve/issues) for our ongoing feature wishlists.

## Examples

**Note both projects are in active development!**

- An example query retrieving GenNotes data: http://gennotes.herokuapp.com/api/variant/b37-1-100672060-T-T/
- [Genevieve genome report screenshot](https://cloud.githubusercontent.com/assets/82631/8336384/13b34ae4-1a72-11e5-8e84-bc47a62ca060.png)

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
    * [As postgres] Create your databasae, e.g.: `createdb mydb`
    * [As postgres] Create your database user, e.g.: `createuser -P myuser`. Remember the password used, you'll need it in your configuration later!
    * [As postgres] Log in to PostgreSQL, e.g.: `psql mydb`
    * **RECOMMENDED WITH WARNING:** The following grants **superuser** status to your database user:
      * [As postgres, in psql] `ALTER ROLE myuser WITH SUPERUSER;`
    * **ALTERNATE APPROACH:** If superuser isn't possible, you won't be able to run `python manage.py tests` as the database user won't be able to automatically create the test database. You can still set your project up with the following three steps:
      * [As postgres, in psql] Add HStore extension to this database: `CREATE EXTENSION IF NOT EXISTS "hstore";`
      * [As postgres, in psql] Grant database privileges to your user, e.g.: `GRANT ALL PRIVILEGES ON DATABASE mydb TO myuser`
      * [Later] When you edit your `.env` (see below) make sure to specify `PSQL_USER_IS_SUPERUSER="False"`
    * Use `\q` to quit psql, and `exit` to log off as the postgres user.
  * *OSX instructions (Homebrew?) invited!*
* **Copy `env.example` to `.env`** (note the leading dot!)
  * Set your `SECRET_KEY` with a random string.
  * Set the `DATABASE_URL` using appropriate PostgreSQL database name, user, and password.
  * The easiest mail set-up is probably to set `EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"`. Emails "sent" by the site will show up in console output.
* **Initialize the database:** `python manage.py migrate`
* **Run the site:** `python manage.py runserver`
* You can now load GenNotes in your web browser by visiting `http://localhost:8000/`.
* You can also interact directly with your site via shell_plus using `python manage.py shell_plus`

### Testing

Test your code changes by running `python manage.py test`.
