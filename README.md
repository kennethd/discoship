# discoship
Create international shipping policies for discogs.com
```
@@@@@@@@@@@@@@@        @@@@@@@@
@@@@@@@@@@@@@@@@@@     @@@@@@@@
@@@@@@@@ @@@@@@@@@@    @@@@@@@@
@@@@@@@@   @@@@@@@@@
@@@@@@@@    @@@@@@@@@  @@@@@@@@      @@@@@@@@           @@@@@@@              @@@@@
@@@@@@@@     @@@@@@@@  @@@@@@@@   @@@@@@@@@@@@@      @@@@@@@@@@@@@      @@@@@@@@@@@@@@@
@@@@@@@@     @@@@@@@@  @@@@@@@@  @@@@@@@@@@@@@@@   @@@@@@@@@@@@@@@@  @@@@@@@@@@@@@@@@@
@@@@@@@@     @@@@@@@@@ @@@@@@@@ @@@@@@@   @@@@@@@  @@@@@@@  @@@@@@@ @@@@@@@@@@@@@@@@@   @@@
@@@@@@@@     @@@@@@@@@ @@@@@@@@ @@@@@@@    @@@@@  @@@@@@@@  @@@@@@@@@@@@@@@@@@@@@@@  @@@@@@@
@@@@@@@@     @@@@@@@@@ @@@@@@@@ @@@@@@@@          @@@@@@@@      @@@@@@@@@@@@@@@@@@ @@@@@@@@@@
@@@@@@@@     @@@@@@@@@ @@@@@@@@  @@@@@@@@@       @@@@@@@@@      @@@@@@@@@@@ @@@@@ @@@@@@@@@@@@
@@@@@@@@     @@@@@@@@@ @@@@@@@@   @@@@@@@@@@     @@@@@@@@@     @@@@@@@@@@@@       @@@@@@@@@@@@@
@@@@@@@@     @@@@@@@@  @@@@@@@@    @@@@@@@@@@@   @@@@@@@@@     @@@@@@@@@@@@  @@   @@@@@@@@@@@@@
@@@@@@@@     @@@@@@@@  @@@@@@@@      @@@@@@@@@@@ @@@@@@@@@     @@@@@@@@@@@@       @@@@@@@@@@@@
@@@@@@@@     @@@@@@@@  @@@@@@@@        @@@@@@@@@@ @@@@@@@@     @@@@@@@@@@@@@@@@@@ @@@@@@@@@@@@
@@@@@@@@    @@@@@@@@   @@@@@@@@          @@@@@@@@ @@@@@@@@      @@@@@@@@@@ @@@@@@@@@@@@@@@@@@
@@@@@@@@    @@@@@@@@   @@@@@@@@ @@@@@@    @@@@@@@  @@@@@@@   @@@@@@@@@@@  @@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@    @@@@@@@@ @@@@@@@@@@@@@@@@@  @@@@@@@@@@@@@@@@@@@   @@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@     @@@@@@@@  @@@@@@@@@@@@@@     @@@@@@@@@@@@@@      @@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@        @@@@@@@@    @@@@@@@@@@@        @@@@@@@@@@       @@@@@@@@@@@@@@
                         __  o                            |            .'  @@@@@
                        /  |/                         \   |   /                       ♪ 
                      _/___|________        ♪      `.  .d88b.   .'       ♪ 
                     /  _______   __\                 d888888b      ♪         ♪ 
   _______          /  /_o_||__| |        --     --  (88888888)  --     --         ♪ 
    \_\_\_\________/___          |           ♪        Y888888Y              ♪            ♪ 
             \         \_________|____________  ♪ .'   `Y88Y'   `.   ♪   _________
              \     ||                         ♪    ♪ /      \    `    ♪        ♪ |
               \  +_||_+   ()  ()     ♪  ┗(･o･)┛ ♪        ♪      ♪     ┌(･o･)┓    |
                \                        ♪  └|∵|┐  ♪  ♪ └|∵|┘  ♪  ♪ ┌|∵|┘     ♪   |
                 \     _  ,,          _        ♪  ┏(･o･)┛   ♪♪  ┗(･o･)┓   ♪      /
 ^^^^^^^^^^^^^^^^ \_.=" )"  "-._____,' ";_______________________________________/_^^^^^^
   ^^^^  ^^^^                                                                  \__|==% ^^
  ^^         ^^^^^^^^       ^^^^ ^^^ ^^^^^       ^^^^^^^^^^  ^         ^^^^
^^^   ^^^^          ^^^^^^^^^^^^          ^^^^     ^^       ^^^^^    ^^       ^^^^^
```

## USPS Shipping Policies
USPS *FCPIS* & *PMI* services are the only rates currently generated.

So far, I personally only have experience with *FCPIS* (First Class Package Int'l).

Discogs does not currently allow creating shipping policies via their API, so
the best this project can do is generate pricing tables for the 20 Country
Price Groups USPS uses to determine rates for international packages, which US
residents can use as a guide when manually creating policies.

### USPS First-Class Package International Service

  * Assumes standard record mailer type boxes (12.5" x 12.5" x 0.5/1.0")
  * Max weight 4LBS (64OZ)

The policy generator will create two price options for *FCPIS*: registered mail
and not-registered.  What "registered" means for international packages varies
by country, it is significantly more expensive, you can read more about it at
https://faq.usps.com/articles/FAQ/What-is-Registered-Mail-International

The other/non-registered *FCPIS* rate generated includes a small fee for a
"Certificate of Mailing", which is a scammy sort of extra receipt service USPS
provides for senders to absolve them of accusations of not sending the
package at all in the case of it becoming "lost in the mail".  It's a small
enough fee ($1.50 at time of writing) that as sender, I feel it to be worth it.

### USPS Priority Mail Internationsl

### USPS Priority Mail Express Internationsl


## Developer Quickstart
Originally, I expected to be able to create & manage shipping policies via the
[Discogs API](https://www.discogs.com/developers/).  Unfortunately that
functionality is not exposed; maybe it's for the best, it could cause a lot of headaches.

Given the limitations, then, there is not much reason to run `discoship` locally,
provided the published rate tables are up to date, but if you want to do it:

### Dependencies
The only dependency is [Python3](https://www.python.org/downloads/), and `bash`
for the install script (which only creates a virtualenv & uses `pip` to install
the package, so probably easy to work around for Windows users).  I think the
oldest `python3` I've tested it with is `3.11`.

### Install
```sh
$ git clone -o github git@github.com:kennethd/discoship.git
$ cd discoship
$ ./bin/install
$ source ./venv-discoship/bin/activate
$ which discoship
```
The last command should output something similar to `/home/kenneth/git/discoship/venv-discoship/bin/discoship`

The install script will have installed some dev tools; to run the unit tests, use `pytest`:
```sh
$ pytest --cov=discoship --verbose --showlocals
```

The `install` script just creates a virtualenv & installs `discoship` and
dependencies into it, if you are on a system without `bash`, just follow along
with the script from the line that looks something like `python3 -m venv ./venv-discoship`

### Ingest
You can now ingest all required data from USPS & populate discogs "ship-to
countries" data:
```sh
$ discoship --info init --all
```
If anything fails, replacing `--info` with `--debug` might provide more insight.

You can re-run specific pieces of the ingest process, see `discoship --help`
and `discoship ingest --help`, `discoship ingest usps --help` etc

### Periodic updates
Because `discoship init --all` recreates the entire database from scratch,
rate change info can be re-ingested specifically:
```sh
$ discoship --info ingest usps --all
```
You probably want to do that on a branch so a PR can be created to merge it upstream.

### Generate policies


## configs

### Mapping record weights and USPS weight-based rate tables

My (admittedly small sample size) experiments packing up records and weighing
them resulted in these settings:
```json
{
  "weight_1_lp_oz": 20,
  "weight_2_lp_oz": 34,
  "weight_3_lp_oz": 42,
  "weight_4_lp_oz": 52,
  "weight_5_lp_oz": 60,
  "weight_6_lp_oz": 70
}
```
Since *FCPIS* max weight is 64oz, I didn't go any higher than that, but for
*PMI* prices have been ingested up to 10lbs.



## ROADMAP

  * Upon receiving my first int'l order, I noticed transaction fees are not applied
    to the subtotal only, but to shipping costs as well -- which comes to about
    50-60&cent; for a typical stateside order, but eating 9% of a $60 shipping
    bill sucks, and inflates the PayPal fees further; considering adding a
    config option to compensate for fees on high int'l shipping costs

## CHANGELOG

### 2025-11-23: version 1.0.0
<dl>
  <dt>Moved `config` table to new `userdata.db`</dt>
  <dd>re-ingested usps rate data can be committed independently of user config</dd>
  <dt>Added `init --all`</dt>
  <dd>Now all the pieces work independently, add convenient post-install "do everything" flag</dt>
</dl>

### 2025-11-20
<dl>
  <dt>Added `./bin/install` & `./bin/clean` scripts</dt>
  <dd>
    Simplified install instructions/procedure.  This project doesn't warrant
    external dependencies for a build system, but if you have `bash`, you have
    the option of using these scripts
  </dd>
</dl>

## AUTHOR
I usually only operate my store when between programming gigs; if the
[store](https://www.discogs.com/seller/kennethd/profile) is open, please buy a
record!  And if you like the code, and have a Python gig, reach out & hire me!

