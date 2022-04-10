import requests
import argparse
from datetime import datetime, timezone
import csv
from time import sleep

OPENSEA_APIKEY = ""

def get_events(start_date, end_date, contractid, cursor='', event_type='successful', **kwargs):
    url = "https://api.opensea.io/api/v1/events"
    query = {"only_opensea": "false", 
             "asset_contract_address": contractid,
             "occurred_before": end_date,
             "occurred_after": start_date,
             "event_type": event_type,
             "cursor": cursor,
             **kwargs
             }

    headers = {
        "Accept": "application/json",
        "X-API-KEY": OPENSEA_APIKEY
    }
    response = requests.request("GET", url, headers=headers, params=query)

    return response.json()
    
def get_assest(contractid,tokenid,):
    url = "https://api.opensea.io/api/v1/asset/"+contractid+"/"+tokenid+"/?include_orders=false"

    headers = {
        "Accept": "application/json",
        "X-API-KEY": OPENSEA_APIKEY
    }
    response = requests.request("GET", url, headers=headers)

    return response.json()

def parse_trait(trait,record):

    name = trait['trait_type']
    record[name] = trait['value']
    
    return record

def fetch_all_traits(record,contractid,tokenid):
    result = list()
    
    next = ''
    fetch = True
    sleep(0.25)
    response = get_assest(contractid,tokenid)
    #    Re-try twice with delays
    if "detail" in response:
        print(response)
        sleep(2)
        response = get_assest(contractid,tokenid)
    if "detail" in response:
        print(response)
        sleep(5)
        response = get_assest(contractid,tokenid)
    #    return record
    for trait in response['traits']:
        record = parse_trait(trait,record)

    return record
    
def parse_event(event):
    record = {}
    asset = event.get('asset')
    if asset == None:
        return None # if there's no asset that means it's not a single NFT transaction so skip this item

    #collection
    record['collection_slug'] = asset['collection']['slug']

    #asset
    record['token_id'] = asset['token_id']

    #traits
    record = fetch_all_traits(record,asset['asset_contract']['address'],asset['token_id'])

    #event
    record['event_time'] = event.get('created_date')
    record['event_quantity'] = event.get('quantity')
    record['event_payment_symbol'] =  None if event.get('payment_token') == None else event.get('payment_token').get('symbol')

    decimals = 18
    if event.get('payment_token') != None:
        decimals = event.get('payment_token').get('decimals')

    price_str = event['total_price']
    print(record)
    try: 
        if len(price_str) < decimals:
            price_str =  "0." + (decimals-len(price_str)) * "0" + price_str
            record['event_total_price'] = float(price_str)
        else:
            record['event_total_price'] = float(price_str[:-decimals] + "." + price_str[len(price_str)-decimals:])
    except:
        print(event)
    return record

def fetch_all_events(start_date, end_date, contractid, pause=1, **kwargs):
    result = list()
    next = ''
    fetch = True

    print(f"Fetching events between {start_date} and {end_date}")
    while fetch:
        response = get_events(int(start_date.timestamp()), int(end_date.timestamp()), contractid, cursor=next, **kwargs)
        #    Re-try twice with delays
        if "detail" in response:
            print(response)
            sleep(2)
            response = get_events(int(start_date.timestamp()), int(end_date.timestamp()), contractid, cursor=next, **kwargs)
        if "detail" in response:
            print(response)
            sleep(5)
            response = get_events(int(start_date.timestamp()), int(end_date.timestamp()), contractid, cursor=next, **kwargs)
        for event in response['asset_events']:
            cleaned_event = parse_event(event)
            
            if cleaned_event != None:
                result.append(cleaned_event)

        if response['next'] is None:
            fetch = False
        else:
            next = response['next']

        sleep(0.25)

    return result

def write_csv(data, filename):
    with open(filename, mode='w', encoding='utf-8', newline='\n') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames = data[0].keys())

        writer.writeheader()
        for event in data:
            writer.writerow(event)   

def valid_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        msg = "Not a valid date: {0!r}".format(s)
        raise argparse.ArgumentTypeError(msg)

def valid_datetime(arg_datetime_str):
    try:
        return datetime.strptime(arg_datetime_str, "%Y-%m-%d %H:%M")
    except ValueError:
        try:
            return datetime.strptime(arg_datetime_str, "%Y-%m-%d")
        except ValueError:
            msg = "Given Datetime ({0}) not valid! Expected format, 'YYYY-MM-DD' or 'YYYY-MM-DD HH:mm'!".format(arg_datetime_str)
            raise argparse.ArgumentTypeError(msg)   

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', "--startdate", help="The Start Date (YYYY-MM-DD or YYYY-MM-DD HH:mm)", required=True, type=valid_datetime)
    parser.add_argument('-e', "--enddate", help="The End Date (YYYY-MM-DD or YYYY-MM-DD HH:mm)", required=True, type=valid_datetime)
    parser.add_argument('-p', '--pause', help='Seconds to wait between http requests. Default: 1', required=False, default=1, type=float)
    parser.add_argument('-o', '--outfile', help='Output file path for saving nft sales record in csv format', required=False, default='./data.csv', type=str)
    parser.add_argument('-c', '--contractid', help='Contract address of collection', required=True, type=str)
    args = parser.parse_args()
    res = fetch_all_events(args.startdate.replace(tzinfo=timezone.utc), args.enddate.replace(tzinfo=timezone.utc), args.pause, args.contractid)

    if len(res) != 0:
        write_csv(res, args.outfile)
    
    print("Done!")

if __name__ == "__main__":
    main()