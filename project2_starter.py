# SI 201 HW4 (Library Checkout System)
# Your name: Syed-Arqam Ahmad
# Your student id: 4772 8485
# Your email: aarqam@umich.edu
# Who or what you worked with on this homework (including generative AI like ChatGPT):
# If you worked with generative AI also add a statement for how you used it.
# e.g.:
# Asked ChatGPT for hints on debugging and for suggestions on overall code structure
#
# Did your use of GenAI on this assignment align with your goals and guidelines in your Gen AI contract? If not, why?
#
# --- ARGUMENTS & EXPECTED RETURN VALUES PROVIDED --- #
# --- SEE INSTRUCTIONS FOR FULL DETAILS ON METHOD IMPLEMENTATION --- #

from bs4 import BeautifulSoup
import re
import os
import csv
import unittest
import requests  # kept for extra credit parity


# IMPORTANT NOTE:
"""
If you are getting "encoding errors" while trying to open, read, or write from a file, add the following argument to any of your open() functions:
    encoding="utf-8-sig"
"""


def load_listing_results(html_path) -> list[tuple]:
    """
    Load file data from html_path and parse through it to find listing titles and listing ids.

    Args:
        html_path (str): The path to the HTML file containing the search results

    Returns:
        list[tuple]: A list of tuples containing (listing_title, listing_id)
    """

    # From what I see the title and id is embedded in this line of the HTML:
    ''' <div class="t1jojoys dir dir-ltr" id="title_1944564" 
        data-testid="listing-card-title">Loft in Mission District</div>'''
    
    ''' So what we can do is find all div classes with the attribute value listing-card-title 
        since it doesn't change across listings. Using that we'll also extract the title_id and
        replace the 'title_id' part with just an empty string, extracting only the id ''' 
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    # open the html path as file
    with open(html_path, 'r', encoding="utf-8-sig") as file: 
        soup = BeautifulSoup(file.read(), "html.parser") # have beautiful soup read the file with html parser

    # make an empty list to hold the values for tuples of listing and title.
    listing_and_title = []

    #again we'll use beautiful soup to find all these div classes with the specific attribute for listing-card-title
    title_divs = soup.find_all("div", attrs={"data-testid":"listing-card-title"})

    #now go through each and return the listing-card-title as the title and id attribute as title_id, replace all "title_id" with ""
    for div in title_divs:
        title = div.get_text(strip=True)

        full_id = div.get("id") #gives us: "title_=????????"

        if isinstance(full_id, str):
            listing_id = full_id.split("title_")[1] 
            listing_and_title.append((title, listing_id)) # we'll append this as a tuple to our list

    return listing_and_title

    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def get_listing_details(listing_id) -> dict:
    """
    Parse through listing_<id>.html to extract listing details.

    Args:
        listing_id (str): The listing id of the Airbnb listing

    Returns:
        dict: Nested dictionary in the format:
        {
            "<listing_id>": {
                "policy_number": str,
                "host_type": str,
                "host_name": str,
                "room_type": str,
                "location_rating": float
            }
        }
    """
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    base_dir = os.path.abspath(os.path.dirname(__file__))
    file_path = os.path.join(base_dir, "html_files", f"listing_{listing_id}.html") # we'll join each "listing_" with the id "??????"

    with open(file_path, "r", encoding="utf-8-sig") as file: # open the file path with the listing path
        soup = BeautifulSoup(file.read(), "html.parser") # read the file

    text = soup.get_text() # get all the text using soup

    ''' Search for Policy Number '''
    if "Pending" in text:
        policy_number = "Pending"
    elif "Exempt" in text:
        policy_number = "Exempt"
    else: 
        match = re.search(r"(STR-\d+|\d+-\d+STR)", text) # use regex to find any word character or - (zero or more) followed by STR followed by the same beginning condition
        if match:
            policy_number = match.group()
        else:
            policy_number = ""
    ''' Search for Policy Number '''

    ''' Search for Host Type '''
    if  "Superhost" in text:
        host_type = "Superhost"
    else:
        host_type = "regular"
    ''' Search for Host Type '''

    ''' Search for Host Name '''
    host_name = ""

    for tag in soup.find_all("h2"): # hosted by is stored in an h2
        text_line = tag.get_text(strip=True) # get text for that h2 which should contain "hosted by" somewhere in there

        if "hosted by" in text_line.lower():
            parts = re.split(r"hosted by", text_line, flags=re.IGNORECASE) # used genAI to get syntax on ignoring the case of the alphabetic chars
            if len(parts) > 1:
                host_name = parts[1].strip()
            break
    ''' Search for Host Name '''

    ''' Search for Room Type '''
    middle = ""
    for tag in soup.find_all("h2"):
        line = tag.get_text(strip=True)
        if "hosted by" in line.lower():
            middle = line
            break

    if middle:
        first_word = middle.split()[0]
    else:
        first_word = ""

    if first_word == "Private":
        room_type = "Private Room"
    elif first_word == "Shared":
        room_type = "Shared Room"
    else:
        room_type = "Entire Room"

    ''' Search for Room Type '''

    ''' Search for Rating '''
    location_rating = 0.0 # set by default


    full_text = soup.get_text(separator=" ", strip=True)

    match = re.search(r"Location\s*(\d\.\d+)", full_text) # we'll use regex to find the decimal number

    if match:
        location_rating = float(match.group(1)) # must convert to float before assigning it into the field

    ''' Search for Rating '''

    # return dict: 
    return {
        listing_id: {
            "policy_number": policy_number,
            "host_type": host_type,
            "host_name": host_name,
            "room_type": room_type,
            "location_rating": location_rating
        }
    }

    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def create_listing_database(html_path) -> list[tuple]:
    """
    Use prior functions to gather all necessary information and create a database of listings.

    Args:
        html_path (str): The path to the HTML file containing the search results

    Returns:
        list[tuple]: A list of tuples. Each tuple contains:
        (listing_title, listing_id, policy_number, host_type, host_name, room_type, location_rating)
    """
    '''
    first we'll get the listings results (listing_title, listing_id)
    for each listing_title and listing_id in listings, we'll get the listing details
    based on each of those, we can make a dict with tuples of the full listing 
    we'll put the full listing into a database list
    '''
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    database = [] # our empty database will get filled

    listings = load_listing_results(html_path) #load the listing results, should give us tuple (listing_title, listing_id)
    
    for listing_title, listing_id in listings:
        details_dict = get_listing_details(listing_id)
        inner_dict = details_dict[listing_id]

        # make a tuple with the original listing tuple and the dictionary values
        row = (listing_title, listing_id, 
               inner_dict["policy_number"],
               inner_dict["host_type"],
               inner_dict["host_name"],
               inner_dict["room_type"],
               inner_dict["location_rating"]
               )
        
        database.append(row) # append the row to the database and return it

    return database
    
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def output_csv(data, filename) -> None:
    """
    Write data to a CSV file with the provided filename.

    Sort by Location Rating (descending).

    Args:
        data (list[tuple]): A list of tuples containing listing information
        filename (str): The name of the CSV file to be created and saved to

    Returns:
        None
    """
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    # we can sort via lambda which will take last item in data and sort in reverse order
    sorted_data = sorted(data, key=lambda x: x[6], reverse=True) 

    # open a file for writing
    with open(filename, 'w', encoding="utf-8-sig") as file:
        writer = csv.writer(file)

        # our header
        writer.writerow([
            "Listing Title",
            "Listing ID",
            "Policy Number",
            "Host Type",
            "Host Name"
            "Room Type"
            "Location Rating"
        ])
        
        # for each row in the data, we'll write this into our CSV
        for row in sorted_data:
            writer.writerow(row)
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def avg_location_rating_by_room_type(data) -> dict:
    """
    Calculate the average location_rating for each room_type.

    Excludes rows where location_rating == 0.0 (meaning the rating
    could not be found in the HTML).

    Args:
        data (list[tuple]): The list returned by create_listing_database()

    Returns:
        dict: {room_type: average_location_rating}
    """
    '''
    room type is in row[5]
    rating is in row[6]

    we'll group by room type and ignore all 0.0 ratings
    then we'll take an avarage and store it and return it in the dict
    '''
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    totals = {}
    counts = {}

    # retrieve room type and rating
    for row in data:
        room_type = row[5]
        rating = row[6]

        # skip if 0.0 rating
        if rating == 0.0:
            continue

        # if the room type isn't in the dict then we initialize it to zero
        if room_type not in totals:
            totals[room_type] = 0
            counts[room_type] = 0

        # else we add the rating to the totals and increment the count
        totals[room_type] += rating
        counts[room_type] += 1

    # now we'll caclulate average because once out of the loop we should have all values
    averages = {}

    # find avg
    for room_type in totals:
        averages[room_type] = totals[room_type] / counts[room_type]

    return averages    
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def validate_policy_numbers(data) -> list[str]:
    """
    Validate policy_number format for each listing in data.
    Ignore "Pending" and "Exempt" listings.

    Args:
        data (list[tuple]): A list of tuples returned by create_listing_database()

    Returns:
        list[str]: A list of listing_id values whose policy numbers do NOT match the valid format
    """
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    pass
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


# EXTRA CREDIT
def google_scholar_searcher(query):
    """
    EXTRA CREDIT

    Args:
        query (str): The search query to be used on Google Scholar
    Returns:
        List of titles on the first page (list)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    pass
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


class TestCases(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.abspath(os.path.dirname(__file__))
        self.search_results_path = os.path.join(self.base_dir, "html_files", "search_results.html")

        self.listings = load_listing_results(self.search_results_path)
        self.detailed_data = create_listing_database(self.search_results_path)

    def test_load_listing_results(self):
        # CHECK: Check that the number of listings extracted is 18.
        # CHECK: Check that the FIRST (title, id) tuple is  ("Loft in Mission District", "1944564").
        # DONE
        self.assertEqual(len(self.listings), 18)
        self.assertEqual(self.listings[0], ("Loft in Mission District", "1944564"))

    def test_get_listing_details(self):
        html_list = ["467507", "1550913", "1944564", "4614763", "6092596"]

        # CHECK: Call get_listing_details() on each listing id above and save results in a list.
        results = []
        for listing_id in html_list:
            results.append(get_listing_details(listing_id))

        # CHECK: Spot-check a few known values by opening the corresponding listing_<id>.html files.
        # 1) Check that listing 467507 has the correct policy number "STR-0005349".
        self.assertEqual(
            results[0]["467507"]["policy_number"], "STR-0005349"
        )
        # 2) Check that listing 1944564 has the correct host type "Superhost" and room type "Entire Room".
        self.assertEqual(
            results[2]["1944564"]["host_type"], "Superhost"
        )

        self.assertEqual(
            results[2]["1944564"]["room_type"], "Entire Room"
        )

        # 3) Check that listing 1944564 has the correct location rating 4.9.
        self.assertEqual(
            results[2]["1944564"]["location_rating"], 4.9
        )

        

    def test_create_listing_database(self):
        # CHECK: Check that each tuple in detailed_data has exactly 7 elements:
        # (listing_title, listing_id, policy_number, host_type, host_name, room_type, location_rating)
        for row in self.detailed_data:
            self.assertEqual(len(row), 7)

        # CHECK: Spot-check the LAST tuple is ("Guest suite in Mission District", "467507", "STR-0005349", "Superhost", "Jennifer", "Entire Room", 4.8).
        self.assertEqual(
            self.detailed_data[-1], 
            ("Guest suite in Mission District",
             "467507",
             "STR-0005349",
             "Superhost",
             "Jennifer",
             "Entire Room",
             4.8
            )
        )
        

    def test_output_csv(self):
        out_path = os.path.join(self.base_dir, "test.csv")

        # CHECK: Call output_csv() to write the detailed_data to a CSV file.
        output_csv(self.detailed_data, out_path)
        # CHECK: Read the CSV back in and store rows in a list.
        with open(out_path, "r", encoding="utf-8-sig") as file:
            reader = csv.reader(file)
            rows = list(reader)
        # CHECK: Check that the first data row matches ["Guesthouse in San Francisco", "49591060", "STR-0000253", "Superhost", "Ingrid", "Entire Room", "5.0"].
        self.assertEqual(
            rows[1],
            ["Guesthouse in San Francisco",
            "49591060",
            "STR-0000253",
            "Superhost",
            "Ingrid",
            "Entire Room",
            "5.0"]
        )

        os.remove(out_path)

    def test_avg_location_rating_by_room_type(self):
        # CHECK: Call avg_location_rating_by_room_type() and save the output.
        averages = avg_location_rating_by_room_type(self.detailed_data)

        # CHECK: Check that the average for "Private Room" is 4.9.
        self.assertAlmostEqual(averages["Private Room"], 4.9)

    def test_validate_policy_numbers(self):
        # TODO: Call validate_policy_numbers() on detailed_data and save the result into a variable invalid_listings.
        # TODO: Check that the list contains exactly "16204265" for this dataset.
        pass


def main():
    detailed_data = create_listing_database(os.path.join("html_files", "search_results.html"))
    output_csv(detailed_data, "airbnb_dataset.csv")


if __name__ == "__main__":
    main()
    unittest.main(verbosity=2)