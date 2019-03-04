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
    errors = []

    count = 0
    successes = 0

    for room in (r.json()['d'])['results']:
        values_as_html_links.append(room['FieldValuesAsHtml']['__deferred']['uri'])
        count += 1

    print("Found " + str(count) + " rooms.\n")
    current_room = ""

    for link in values_as_html_links:
        try:
            request = s.get(link)
            soup = (request.json()['d'])

            # Parsing room name.
            name = soup['Room_x005f_x0020_x005f_Identifier']
            current_room = name
            identifier = name.split('(', 1)[-1].replace(')', '')
            staircase_identifier = ''

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

            # Parsing bathroom sharing.
            bathroom_sharing = int(soup['Number_x005f_x0020_x005f_of_x005f_x0020_x005f_people_x005f_x00'])

            # Parsing contract length.
            contract_length = int(soup['ContractLength'])

            # Parsing facing court.
            facing_court = soup['Facing_x005f_x0020_x005f_Court'] == "Yes" and not identifier.__contains__('LR')

            # Parsing facing Lensfield Road / Regent St.
            facing_lensfield = soup['Facing_x005f_x0020_x005f_Lensfield_x005f_x0020_x005f_Roa'] == "Yes"

            # Parsing in ballot.
            in_ballot = soup['IntheBallot'] == "Yes"
            occupancy = soup['Occupancy']

            # If room already exists.
            try:
                room = Room.objects.get(identifier=identifier)

                print(identifier)
                if floor != room.floor:
                    print("Old floor: %s, New floor: %s", room.floor, floor)

                if size != room.size:
                    print("Old size: %s, New size: %s", room.size, size)

                if is_double_bed != room.is_double_bed:
                    print("Old double bed: %s, New double bed: %s", room.is_double_bed, is_double_bed)

                if is_ensuite != room.is_ensuite:
                    print("Old ensuite: %s, New ensuite: %s", room.is_ensuite, is_ensuite)

                if year_last_renovated_kitchen != room.kitchen_last_renovated:
                    print("Old kitchen: %s, New kitchen: %s", room.kitchen_last_renovated, year_last_renovated_kitchen)

                if year_last_renovated_bathroom != room.bathroom_last_renovated:
                    print("Old bathroom: %s, New bathroom: %s", room.bathroom_last_renovated,
                          year_last_renovated_bathroom)

                if year_last_renovated_room != room.room_last_renovated:
                    print("Old room: %s, New room: %s", room.room_last_renovated, year_last_renovated_room)

                if bathroom_sharing != room.bathroom_sharing:
                    print("Old bathroom sharing: %s, New bathroom sharing: %s", room.bathroom_sharing, bathroom_sharing)

                if facing_lensfield != room.faces_lensfield:
                    print("Old Lensfield: %s, New Lensfield: %s", room.faces_lensfield, facing_lensfield)

                if facing_court != room.faces_court:
                    print("Old court: %s, New court: %s", room.faces_court, facing_court)
                print()

            except Room.DoesNotExist:
                # room = Room()
                print("Room does not exist", identifier)
            """
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
            if contract_length > 0:
                room.contract_length = contract_length
            if room.sort_number is None:
                room.sort_number = number
            room.bathroom_sharing = min(bathroom_sharing, 5)
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
            successes += 1
            """
        except Exception as e:
            errors.append(current_room + " - " + str(e))
    print("=== IMPORT REPORT ===")
    print("Total Rooms:", str(count))
    print("Succeeded:", str(successes))
    print("Failed:", str(len(errors)))

    print()
    for error in errors:
        print(error)
        print()


def write_bands():
    s = sharepy.connect("downingcollege.sharepoint.com", sharepoint_user, sharepoint_password)
    r = s.get(
        "https://downingcollege.sharepoint.com/sites/RoomsBrowserJCR/_api/web/lists/GetByTitle('RoomsData')/Items?$select=Room_x0020_Identifier,New_x0020_Room_x0020_Band")
    context_request = s.post("https://downingcollege.sharepoint.com/sites/RoomsBrowserJCR/_api/contextinfo")

    update_headers = {
        "Accept": "application/json; odata=verbose",
        "Content-Type": "application/json; odata=verbose",
        "odata": "verbose",
        "X-RequestForceAuthentication": "true",
        "X-RequestDigest": context_request.json()['d']['GetContextWebInformation']['FormDigestValue'],
        "IF-MATCH": "*",
        "X-HTTP-Method": "MERGE"
    }

    print(context_request.json()['d']['GetContextWebInformation']['FormDigestValue'])

    for room in (r.json()['d'])['results']:

        name = room['Room_x0020_Identifier']
        identifier = name.split('(', 1)[-1].replace(')', '')

        try:
            r = Room.objects.get(identifier=identifier)
            if r.type == 4:
                continue
            else:
                uri = (room['__metadata'])['uri']
                s.post(uri, json={"__metadata": {"type": "SP.Data.RoomsListItem"},
                                         'New_x0020_Room_x0020_Band': r.new_band.band_name}, headers=update_headers)
        except Room.DoesNotExist:
            print("Couldn't find room", identifier)
