#!/usr/bin/python3

#
# ULEZ_Checker
#
# Copyright (c) 2022 Daniel Dean <dd@danieldean.uk>.
#
# Licensed under The MIT License a copy of which you should have
# received. If not, see:
#
# http://opensource.org/licenses/MIT
#

import requests
import json
from requests import HTTPError


def check_vrm(vrm):
    """ Check a Vehicle Registration Mark (VRM) for ULEZ compliance.

    If a repeat request for the same VRM the previous lookup response is returned.

    Args:
        vrm (str): VRM to check.

    Raises:
        ValueError: If supplied VRM is invalid.
        HTTPError: If an error occurred during the request.

    Returns:
        dict: Lookup response results.
    """

    vrm = vrm.replace(' ', '').upper()

    if vrm.isalnum():

        content = {
            "vrmLookupRequest":
                {
                    "vRM": vrm,
                    "country": "UK",
                    "date": {}
                }
        }

        r = requests.post(
            'https://mobileapim.tfl.gov.uk/Prod/unirucCapitaFacade/VRMLookup',
            json.dumps(content),
            headers={
                'accept': 'application/json',
                'content-type': 'application/json'
            },
        )

        if r.status_code == 200:
            vrm_response = json.loads(r.text)
            if vrm_response['vrmLookupResponse']['vehicleDetails']['make'] == '':
                raise ValueError('VRM is invalid: ' + vrm)
            else:
                vrm_response['vrmLookupResponse']['vehicleDetails']['vrm'] = vrm
                return vrm_response
        else:
            r.raise_for_status()

    else:
        raise ValueError('VRM is invalid: ' + vrm)


def to_bool(number):
    """ Convert a '1' to True and anything else to False.

    Args:
        number (int): A number to convert.

    Returns:
        bool: '1' for True, False for anything else.
    """
    if number == 1:
        return True
    else:
        return False


def pretty_print(vrm_response):
    """ Pretty print a lookup response.

    For use when running as a command line tool.

    Args:
        vrm_response (dict): Lookup response results.
    """
    lr = vrm_response['vrmLookupResponse']
    print(
        "\n-----------------------------------------\n"
        f"VRM: {lr['vehicleDetails']['vrm']}\n"
        f"Make: {lr['vehicleDetails']['make']}\n"
        f"Model: {lr['vehicleDetails']['model']}\n"
        f"Colour: {lr['vehicleDetails']['colour']}\n"
        f"Tax Code: {lr['vehicleDetails']['taxCode']}\n"
        f"Chargeability:\n"
        f"    Congestion: {to_bool(lr['vehicleDetails']['chargeability']['isCcChargeable'])}\n"
        f"    LEZ: {to_bool(lr['vehicleDetails']['chargeability']['isLezChargeable'])}\n"
        f"    ULEZ: {to_bool(lr['vehicleDetails']['chargeability']['isUlezChargeable'])}\n"
        f"    ES: {to_bool(lr['vehicleDetails']['chargeability']['isEsChargeable'])}\n"
        f"Auto Pay: {lr['vehicleDetails']['inAutoPay']}\n"
        f"Auto Pay Exceptions: {lr['vehicleDetails']['inAutoPayExceptions']}\n"
        f"Congestion Charge 100% Discounted: {lr['vehicleDetails']['isCc100PcDiscounted']}\n"
        f"ULEZ 100% Discounted: {lr['vehicleDetails']['isUlez100PcDiscounted']}\n"
        f"ULEZ Exempt: {to_bool(lr['vehicleDetails']['isULEZExempt'])}\n"
        f"ULEZ Vehicle Type List: {lr['vehicleDetails']['uLEZVehicleListType']}\n"
        f"ULEZ Non-Chargeable: {to_bool(lr['vehicleDetails']['isULEZNonChargeable'])}\n"
        "-----------------------------------------\n"
    )


def main():
    """ Run as a command line tool.
    """
    while True:
        print('Enter a vehicle registration mark to check: ', end='')
        vrm = input()
        try:
            vrm_response = check_vrm(vrm)
            pretty_print(vrm_response)
        except (ValueError, HTTPError) as err:
            print('An error occurred -', err)


if __name__ == '__main__':
    main()
