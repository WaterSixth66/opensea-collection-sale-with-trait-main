# opensea-collection-sale-with-trait
Python script to retrieve nft event trasactions from OpenSea API on specific collection then retrieve specific traits.

Command execution example:
``` 
> python opensea.py -s "2022-04-06" -e "2022-04-07" -c "0x123b30e25973fecd8354dd5f41cc45a3065ef88c"
``` 
Help for all options:
``` 
> python opensea.py -h
options:
  -h, --help            show this help message and exit
  -s STARTDATE, --startdate STARTDATE
                        The Start Date (YYYY-MM-DD or YYYY-MM-DD HH:mm)
  -e ENDDATE, --enddate ENDDATE
                        The End Date (YYYY-MM-DD or YYYY-MM-DD HH:mm)
  -p PAUSE, --pause PAUSE
                        Seconds to wait between http requests. Default: 1
  -o OUTFILE, --outfile OUTFILE
                        Output file path for saving nft sales record in csv format
  -c CONTRACTADDRESS, --contractid  ADDRESS
			Contract address of collection
```
