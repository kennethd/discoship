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

### Update Data Tables
If you want to update the database, to make sure the rates are current, you'll
want to install the package in "developer mode":
```
kenneth@fado ~/git/discoship (main) $ . ./venv3.11/bin/activate
(venv3.11) kenneth@fado ~/git/discoship (main) $ pip install -e .[dev]
(venv3.11) kenneth@fado ~/git/discoship (main) $ discoship ingest usps --all
```

If you want to contribute the updates back to upstream (this project), make
sure to create a branch first:


## reingest everything from scratch
(debug flag `-d` optional)
```
 $ discoship -d init --db
 $ discoship -d ingest usps --all
 $ discoship -d ingest discogs --destinations
 $ discoship -d ingest countries --iso3166
```

## configs

### Mapping record weights and USPS weight-based rate tables

My (admittedly small sample size) experiments packing up records and weighing
them resulted in these settings:
``` {
  'weight_1_lp_oz': 20,
  'weight_2_lp_oz': 34,
  'weight_3_lp_oz': 42,
  'weight_4_lp_oz': 52,
  'weight_5_lp_oz': 60,
  'weight_6_lp_oz': 70,
}```
Since *FCPIS* max weight is 64oz, I didn't go any higher than that, but for
*PMI* prices have been ingested up to 10lbs.



## ROADMAP

  * Upon receiving my first int'l order, I noticed transaction fees are not applied
    to the subtotal only, but to shipping costs as well -- which comes to about
    50-60&cent; for a typical stateside order, but eating 9% of a $60 shipping
    bill sucks, and inflates the PayPal fees further; considering adding a
    config option to compensate for fees on high int'l shipping costs

## CHANGELOG

### 2025-11-20
<dl>
  <dt>Added `./bin/install` & `./bin/clean` scripts</dt>
  <dd>
    Simplified install instructions/procedure.  This project doesn't warrant
    external dependencies for a build system, but if you have `bash`, you have
    the option of using these scripts
  </dd>
</dl>
