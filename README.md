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


## getting started

Given the limitations of the Discogs API there is not much reason to run
`discoship` locally, provided the published rate tables are up to date, but if
you want to do it:

Clone the repo:
```
$ cd ~/git   # or wherever you keep your repos
$ git clone -o github git@github.com:kennethd/discoship.git
$ cd discoship
```
Install:
```
$ python3 -mvenv ./venv-$(python3 -V | awk '{ split($2, a, "."); print a[1]"."a[2] }')
```
Depending on your version of Python3, your `venv` may be named differently, for me it is `venv-3.11`:
```
kenneth@fado:~/git/discoship (main) $ . ./venv-3.11/bin/activate
(venv-3.11) kenneth@fado:~/git/discoship (main) $ pip install .
```
The first `.` in that first command is a `bash` alias for `source`, if your
shell doesn't recognize it, try using `source`.  There's also no guarantee
your shell is configured to change your prompt upon activating a Python
virtualenv, if you don't see it, try `echo $VIRTUAL_ENV`, or just `which discoship`

Outputs should look something like:
```
(venv-3.10) kenneth@x1:~/git/discoship (main)$ echo $VIRTUAL_ENV
/home/kenneth/git/discoship/venv-3.10
(venv-3.10) kenneth@x1:~/git/discoship (main)$ which discoship
/home/kenneth/git/discoship/venv-3.10/bin/discoship
```

## updating 

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



