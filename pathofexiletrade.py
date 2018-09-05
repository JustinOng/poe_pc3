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

        if "name" in options:
            data["query"]["name"] = options["name"]
        
        if "base" in options:
            data["query"]["type"] = options["base"]

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

        # stage 1: retrieve list of ids of items that match
        r1 = requests.post(f'https://www.pathofexile.com/api/trade/search/{league}', json=data)
        stage1 = json.loads(r1.text)

        if "error" in stage1:
            return stage1
        
        # stage 2: retrieve actual listing of items
        r2 = requests.get(f'https://www.pathofexile.com/api/trade/fetch/{",".join(stage1["result"][0:10])}', params={ "query": stage1["id"] })
        stage2 = json.loads(r2.text)
        print(stage2)