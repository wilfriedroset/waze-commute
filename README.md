# Waze Commute

This is a quick script to poll Waze API to compute commute (both ways) from one
or more addresses to a point of interest. The purpose of this script is to be
used as an [exec
plugin](https://github.com/influxdata/telegraf/tree/master/plugins/inputs/exec)
for [telegraf](https://github.com/influxdata/telegraf). This would allow a user
to have metrics to graph traffic evolution.

The idea came from a personal project to have usable data to see if it is wise
or not to live farther away from the city center to save money.

## Install dependencies
```
$ git clone https://github.com/wilfriedroset/waze-commute; cd waze-commute
$ pip install -r requirements.txt
```

```
$ python waze-commute.py -h
usage: waze-commute.py [-h] --addresses-file ADDRESSES_FILE
                       [--region {EU,US,IL,AU}] --destination DESTINATION
                       [--destination-alias DESTINATION_ALIAS]
                       [--departure-alias DEPARTURE_ALIAS] [--no-real-time]

optional arguments:
  -h, --help            show this help message and exit
  --addresses-file ADDRESSES_FILE
                        path to addresses file
  --region {EU,US,IL,AU}
                        Region is used for address searching
  --destination DESTINATION
                        destination address for which to compute from/to
                        routing
  --destination-alias DESTINATION_ALIAS
                        alias of destination address
  --departure-alias DEPARTURE_ALIAS
                        alias of departure addresses
  --no-real-time        get the time estimate not including current conditions
```

Credit goes to [kovacsbalu](https://github.com/kovacsbalu) for
[WazeRouteCalculator](https://github.com/kovacsbalu/WazeRouteCalculator)

## Configuration

Point of interest address can be define on the command line as there is only
address supported as point of interest. Departure addresses are defined in a
YAML (or JSON) configuration file.

```yaml
---
addresses:
  - address: Pessac, Gironde, France
  - address: Merignac, Gironde, France
  - address: Saint-Emillion, Gironde, France
```

You can add as many key as you want, they will be used as tags. You can add for
example geographic coordinate (latitude/longitude), average m2 price, neighbour
name...


```yaml
---
addresses:
  - address: Pessac, Gironde, France
    river_side: gauche
  - address: Merignac, Gironde, France
    river_side: gauche
  - address: Saint-Emillion, Gironde, France
    river_side: droite
```

## Example

```
$ python waze-commute.py --addresses-file addresses.example.yaml --destination "Bordeaux, Gironde, France"
[
    {
        "duration": 1500,
        "distance": 19362,
        "from": "Pessac, Gironde, France",
        "to": "Bordeaux, Gironde, France",
        "source": "waze",
        "way": "home->office",
        "with_traffic": true,
        "river_side": "gauche"
    },
    {
        "duration": 2521,
        "distance": 44344,
        "from": "Saint-Emillion, Gironde, France",
        "to": "Bordeaux, Gironde, France",
        "source": "waze",
        "way": "home->office",
        "with_traffic": true,
        "river_side": "droite"
    },
    {
        "duration": 1440,
        "distance": 19214,
        "from": "Bordeaux, Gironde, France",
        "to": "Pessac, Gironde, France",
        "source": "waze",
        "way": "office->home",
        "with_traffic": true,
        "river_side": "gauche"
    },
    {
        "duration": 1261,
        "distance": 8881,
        "from": "Merignac, Gironde, France",
        "to": "Bordeaux, Gironde, France",
        "source": "waze",
        "way": "home->office",
        "with_traffic": true,
        "river_side": "gauche"
    },
    {
        "duration": 1321,
        "distance": 8897,
        "from": "Bordeaux, Gironde, France",
        "to": "Merignac, Gironde, France",
        "source": "waze",
        "way": "office->home",
        "with_traffic": true,
        "river_side": "gauche"
    },
    {
        "duration": 2520,
        "distance": 43901,
        "from": "Bordeaux, Gironde, France",
        "to": "Saint-Emillion, Gironde, France",
        "source": "waze",
        "way": "office->home",
        "with_traffic": true,
        "river_side": "droite"
    }
]
```

Duration is in seconds and distance is in meters.

## Running with Telegraf

You can use [telegraf plugin
exec](https://github.com/influxdata/telegraf/tree/master/plugins/inputs/exec) to
run the script periodically and write the points in the back-end of you choice. I
would suggest [influxdb](https://github.com/influxdata/influxdb) as back-end.

Here is an example of telegraf configuration

```toml
[[inputs.exec]]
  commands = ["python /absolute/path/to/waze-commute.py --addresses-file /absolute/path/to/addresses.example.yaml --destination 'Bordeaux, Gironde, France'"]
  name_override = "commute"
  timeout = "4m"
  interval = "5m"
  data_format = "json"
  tag_keys = ["way", "from", "to", "river_side", "source", "with_traffic"]
  tagdrop = ["host"]
```

## Running with docker

Build the image using the provide docker file.
```
$ docker build -t waze-commute .
```

Then execute, use it like [telegraf image](https://hub.docker.com/_/telegraf)

## Bonus: Spawn your influxdb & grafana with docker

```yml
version: '3'
services:

  influxdb:
    image: "influxdb:latest"
    volumes:
      - ./data/influxdb:/var/lib/influxdb
    ports:
      - "8086:8086"
    networks:
      - tsdb

  grafana:
    image: "grafana/grafana:latest"
    ports:
      - "3000:3000"
    volumes:
      - ./data/grafana:/var/lib/grafana
    networks:
      - tsdb
    user: "1000"

  telegraf:
    build:
      context: ./waze-commute
      dockerfile: Dockerfile-telegraf
    command: ["telegraf", "--config-directory", "/etc/telegraf/telegraf.d/"]
    volumes:
      - ./data/telegraf:/etc/telegraf:ro
    networks:
      - tsdb

networks:
  tsdb:
```
