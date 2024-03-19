# euni-cdp
Tools for managing Cargo Deposit Points


To generate a list of all CDPs:
```
./gen-cdp.py > cdp.csv
```
To adjust the parameters or special cases, edit the relevant section in `gen-cdp.py`

To generate a list of the nearest CDP to all highsec systems:
```
./find-cdp.py > nearest.csv
```

Copy and paste these CSV's into the CDP google sheet.
