"""
Gets data from old 'accommodation list'
to populate database.
"""

import requests
import pprint
import re
from requests_ntlm import HttpNtlmAuth
from bs4 import BeautifulSoup
from .models import Room, Staircase, Band

sharepoint_user = "dow-aa\cjo41"
sharepoint_password = "C@m3r0n1492"
sharepoint_url = "https://distro.dow.cam.ac.uk/data/accommodation/_api/Web/"
sharepoint_listname = "accommodation list"
auth = HttpNtlmAuth(sharepoint_user, sharepoint_password)

headers = {
    "Accept": "application/json; odata=verbose",
    "Content-Type": "application/json; odata=verbose",
    "odata": "verbose",
    "X-RequestForceAuthentication": "true",
}

def get_data():
    r = requests.get(
        sharepoint_url + "lists/getbytitle('%s')" % sharepoint_listname,
        auth=auth,
        headers=headers,
        verify=False,
    )
    list_id = r.json()['d']['Id']
    list_itemcount = r.json()['d']['Id']
    api_items_url = sharepoint_url + "Lists(guid'%s')/Items?$top=4000" % list_id
    cur_page = requests.get(api_items_url, auth=auth, headers=headers, verify=False)
    values_as_html_links = []

    count = 0
    successes = 0

    for room in (cur_page.json()['d'])['results']:
        values_as_html_links.append(room['FieldValuesAsHtml']['__deferred']['uri'])
        count += 1

    print("Found " + str(count) + " rooms.\n")

    for link in values_as_html_links:
        try:
            request = requests.get(link, auth=auth)
            soup = BeautifulSoup(request.content, 'xml')

            # Parsing room name.
            name = soup.find('d:College_x005f_x0020_x005f_Room_x005f_x0020_x005f_Locatio').text
            identifier = name.split('(', 1)[-1].replace(')', '')
            staircase_identifier = ''
            print(identifier)

            if identifier[len(identifier)-1].isdigit():
                staircase_identifier = identifier[0:len(identifier)-2]
                number = identifier[len(identifier)-2:len(identifier)]
                if number[0] == '0':
                    number = number[1:len(number)]
            else:
                staircase_identifier = identifier[0:len(identifier)-3]
                number = identifier[len(identifier)-3:len(identifier)]
                if number[0] == '0':
                    number = number[1:len(number)]

            # Parsing disabled facilities.
            disabled_facilities = soup.find('d:Disabled_x005f_x0020_x005f_Facilities').text == "Yes"

            # Parsing floor.
            floor_str = soup.find('d:Floor').text
            floor = 0
            if floor_str == "Ground":
                floor = 1
            elif floor_str == "First":
                floor = 2
            elif floor_str == "Second":
                floor = 3

            # Parsing size.
            size = float(soup.find('d:Room_x005f_x0020_x005f_Size').text)

            # Parsing band.
            band_str = soup.find('d:Rent_x005f_x0020_x005f_Band').text
            band = band_str.replace('Band ', '')

            # Parsing bed.
            is_double_bed = soup.find('d:Beds').text == "Double"

            # Parsing ensuite.
            is_ensuite = soup.find('d:En_x005f_x002d_x005f_suite').text == "Yes"

            # Parsing in ballot.
            in_ballot = soup.find('d:JCR_x005f_x0020_x005f_Ballot_x005f_x0020_x005f_2018').text == "Yes"

            # If room already exists.
            try:
                room = Room.objects.get(identifier=identifier)

            except Room.DoesNotExist:
                room = Room()
            room.identifier = identifier
            room.room_number = number
            room.floor = floor
            room.has_disabled_facilities = disabled_facilities
            room.band = Band.objects.get(band_name=band)
            room.size = size
            room.is_double_bed = is_double_bed
            room.is_ensuite = is_ensuite
            room.type = 2 if in_ballot else 3

            try:
                staircase = Staircase.objects.get(identifier=staircase_identifier)
            except Staircase.DoesNotExist:
                staircase = Staircase()
                staircase.identifier = staircase_identifier
                staircase.name = "ToBeNamedAndSetContractLength"
                staircase.contract_length = 0
                staircase.save()

            room.staircase = staircase
            room.save()

        except:
            print("Failed to get data at " + link)
