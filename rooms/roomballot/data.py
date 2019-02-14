"""
Gets data from 'RoomsData' list on SharePoint Online
to populate database.
Author Cameron O'Connor
"""

from .models import Room, Staircase, Band
from rooms.settings import SHAREPOINT_USERNAME, SHAREPOINT_PASSWORD
import sharepy

sharepoint_user = SHAREPOINT_USERNAME
sharepoint_password = SHAREPOINT_PASSWORD
sharepoint_url = "https://downingcollege.sharepoint.com/sites/RoomsBrowserJCR/_api/Web/"
sharepoint_listname = "RoomsData"


def get_data():
    s = sharepy.connect("downingcollege.sharepoint.com", sharepoint_user, sharepoint_password)
    r = s.get(
        "https://downingcollege.sharepoint.com/sites/RoomsBrowserJCR/_api/web/lists/GetByTitle('%s')/Items?$top=4000"
        % sharepoint_listname)

    values_as_html_links = []

    count = 0

    for room in (r.json()['d'])['results']:
        values_as_html_links.append(room['FieldValuesAsHtml']['__deferred']['uri'])
        count += 1

    print("Found " + str(count) + " rooms.\n")

    for link in values_as_html_links:
        try:
            request = s.get(link)
            soup = (request.json()['d'])

            # Parsing room name.
            name = soup['Room_x005f_x0020_x005f_Identifier']
            print(name)
            identifier = name.split('(', 1)[-1].replace(')', '')
            staircase_identifier = ''
            print(identifier)

            if identifier[len(identifier) - 1].isdigit():
                staircase_identifier = identifier[0:len(identifier) - 2]
                number = identifier[len(identifier) - 2:len(identifier)]
                if number[0] == '0':
                    number = number[1:len(number)]
            else:
                staircase_identifier = identifier[0:len(identifier) - 3]
                number = identifier[len(identifier) - 3:len(identifier)]
                if number[0] == '0':
                    number = number[1:len(number)]

            # Parsing disabled facilities.
            disabled_facilities = soup['DisabledFacilities'] == "Yes"

            # Parsing floor.
            floor_str = soup['Floor']
            floor = int(floor_str) + 1

            # Parsing size.
            size = float(soup['RoomSize'])

            # Parsing band.
            band = soup['Room_x005f_x0020_x005f_Band']

            # Parsing bed.
            is_double_bed = soup['DoubleBed'] == "Yes"

            # Parsing ensuite.
            is_ensuite = soup['Ensuite'] == "Yes"

            # Parsing year bathroom last renovated.
            year_last_renovated_bathroom = int(soup['Yearlastrenovatedbathroom'].replace(',', ''))

            # Parsing year kitchen last renovated.
            year_last_renovated_kitchen = int(soup['YearlastrenovatedKitchen'].replace(',', ''))

            # Parsing year room last renovated.
            year_last_renovated_room = int(soup['Yearlastrenovatedroom'].replace(',', ''))

            # Parsing contract length.
            contract_length = int(soup['ContractLength'])

            # Parsing facing court.
            facing_court = soup['Facing_x005f_x0020_x005f_Court'] == "Yes"

            # Parsing facing Lensfield Road / Regent St.
            facing_lensfield = soup['Facing_x005f_x0020_x005f_Lensfield_x005f_x0020_x005f_Roa'] == "Yes"

            # Parsing in ballot.
            in_ballot = soup['IntheBallot'] == "Yes"
            occupancy = soup['Occupancy']

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
            room.faces_court = facing_court
            room.faces_lensfield = facing_lensfield
            room.bathroom_last_renovated = year_last_renovated_bathroom
            room.room_last_renovated = year_last_renovated_room
            room.kitchen_last_renovated = year_last_renovated_kitchen
            room.contract_length = contract_length
            room.sort_number = number
            if occupancy == 'UG':
                room.type = 2 if in_ballot else 3
            elif occupancy == 'Fresher':
                room.type = 1
            else:
                room.type = 4

            try:
                staircase = Staircase.objects.get(identifier=staircase_identifier)
            except Staircase.DoesNotExist:
                staircase = Staircase()
                staircase.identifier = staircase_identifier
                staircase.name = "ToBeNamed"
                staircase.contract_length = 0
                staircase.save()

            room.staircase = staircase
            room.save()
        except:
            print("Failed to get data at %s" % link)
