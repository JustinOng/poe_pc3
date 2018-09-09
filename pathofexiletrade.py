import requests
import json

class Trade:
    def query(self, league, options):
        """
            options should be a dict with the following optional properties:
            name
            base
            quality_min
            quality_max
        """
        data = {
            "query": {
                "status": {
                    "option": "online"
                }
            },
            "sort": {
                "price": "asc"
            }
        }

        if "name" in options and options["name"]:
            data["query"]["name"] = options["name"]
        
        if "base" in options and options["base"]:
            data["query"]["type"] = options["base"]
        
        if "term" in options and options["term"]:
            data["query"]["term"] = options["term"]

        if "quality_min" in options or "quality_max" in options:
            data["query"]["filters"] = {
                    "misc_filters": {
                        "disabled": False,
                        "filters": {
                            "quality": {}
                        }
                    }
                }

            if "quality_min" in options:
                data["query"]["filters"]["misc_filters"]["filters"]["quality"]["min"] = options["quality_min"]
            
            if "quality_max" in options:
                data["query"]["filters"]["misc_filters"]["filters"]["quality"]["max"] = options["quality_max"]

        print(data["query"])
        # stage 1: retrieve list of ids of items that match
        r1 = requests.post(f'https://www.pathofexile.com/api/trade/search/{league}', json=data)
        stage1 = json.loads(r1.text)

        if "error" in stage1:
            return stage1
        
        if len(stage1["result"]) == 0:
            print(stage1)
            return {
                "error": {
                    "message": "No items found."
                }
            }
        
        # stage 2: retrieve actual listing of items
        r2 = requests.get(f'https://www.pathofexile.com/api/trade/fetch/{",".join(stage1["result"][0:10])}', params={ "query": stage1["id"] })
        stage2 = json.loads(r2.text)

        if "error" in stage2:
            return stage2

        item_name = False
        # stores prices in the format [[amount, currency, count]]
        prices = []
        for item in stage2["result"]:
            if not item_name:
                item_name = f'{item["item"]["name"]} {item["item"]["typeLine"]}'
            
            listing_price = item["listing"]["price"]
            if len(prices) and prices[-1][0] == listing_price["amount"] and prices[-1][1] == listing_price["currency"]:
                prices[-1][2] += 1
            else:
                prices.append([listing_price["amount"], listing_price["currency"], 1])
        
        str_prices = []

        for a in prices:
            if a[2] > 1:
                str_prices.append(f'{a[0]} {a[1]} ({a[2]})')
            else:
                str_prices.append(f'{a[0]} {a[1]}')

        return {
            "result": f'{item_name}: {", ".join(str_prices)}'
        }
