#!/usr/bin/python3

import argparse
import json
import logging

import WazeRouteCalculator


def parse_cli():
    """Parse command line"""
    parser = argparse.ArgumentParser()

    parser.add_argument('--addresses-file', help='path to addresses file',
                        type=argparse.FileType('r', encoding='UTF-8'), required=True)

    parser.add_argument('--region', help='Region is used for address searching',
                        dest='region',
                        default='EU', choices=['EU', 'US', 'IL', 'AU'])

    parser.add_argument('--destination', help='destination address for which to compute from/to routing',
                        dest='destination', required=True)

    parser.add_argument('--destination-alias', help='alias of destination address',
                        default='office',
                        dest='destination_alias')

    parser.add_argument('--departure-alias', help='alias of departure addresses',
                        default='home',
                        dest='departure_alias')

    parser.add_argument('--no-real-time', help='get the time estimate not including current conditions',
                        dest='real_time',
                        default=True,
                        action='store_false')

    parser.add_argument('-d', '--debug',
                        help='Print lots of debugging statements',
                        action='store_const', dest='loglevel',
                        const=logging.DEBUG,
                        default=logging.WARNING)

    parser.add_argument('-v', '--verbose',
                        help='Be verbose',
                        action='store_const', dest='loglevel',
                        const=logging.INFO)

    parser.add_argument('-q', '--quiet',
                        help='Be quiet',
                        action='store_const', dest='loglevel',
                        const=logging.CRITICAL)

    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel)
    return args


def compute(departure_address, destination_address, region='EU', real_time=True):
    """Compute commute duration

    :param departure_address: departure address to compute commute (string)
    :param destination_address: destination address to compute commute (string)
    :param region: Region is used for address searching, choice is EU, US, IL, AU (string)
    :param real_tine: compute commute with real time data
    :returns: commute (dict)
    """
    logging.debug('computing route from %s -> %s in %s with real_time=%s',
                  departure_address, destination_address, region, real_time)

    route = WazeRouteCalculator.WazeRouteCalculator(
        departure_address, destination_address, region, log_lvl=None)

    route_time, route_distance = route.calc_route_info()
    minutes, seconds = divmod(route_time, 1)  # split integer and decimal part

    commute = {
        'duration': round(minutes * 60.0 + seconds),  # min --> seconds
        'distance': round(route_distance * 1000),  # km --> m
        'from': departure_address, 'to': destination_address, 'source': 'waze'
    }

    return commute


def main():
    """ The main """
    args = parse_cli()
    data = []
    addresses = json.load(args.addresses_file)

    for address in addresses.get('addresses', []):
        tags = address.copy()
        departure_address = tags.pop('address')
        ways = [(departure_address, args.departure_alias, args.destination, args.destination_alias),
                (args.destination, args.destination_alias, departure_address, args.departure_alias)]

        for departure, departure_alias, destination, destination_alias in ways:
            try:
                commute = compute(departure, destination,
                                  args.region, args.real_time)
                # Add extra-tags
                commute.update({'way': '%s->%s' % (departure_alias, destination_alias),
                                'with_traffic': args.real_time})
                commute.update(tags)
                data.append(commute)
            except WazeRouteCalculator.WRCError as err:
                logging.error('Failed to compute route from: %s to: %s. reason: %s',
                              departure, destination, err)

    print(json.dumps(data, indent=4))


if __name__ == '__main__':
    main()
