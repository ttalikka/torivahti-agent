# Basic imports
import json
import os
import sys

here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(here, "./vendored"))

# Vendored imports
import requests
import boto3
from bs4 import BeautifulSoup
import stringlibrary

# Base variables
TOKEN = os.environ["TELEGRAM_TOKEN"]
BASE_URL = "https://api.telegram.org/bot{}".format(TOKEN)
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(stringlibrary.DYNAMODB_TABLE)

# Event handler
def hello(event, context):
    jobs = table.scan()
    for n in jobs["Items"]:
        # showLatest(n)
        showNew(n)

    return {"statusCode": 200}


# Returns the latest item with the search query (this is not currently used)
def showLatest(item):
    print(item)
    # Fetch the items from Tori, soupify the results
    r = requests.get("https://www.tori.fi/koko_suomi?q={}".format(item["searchQuery"]))
    soup = BeautifulSoup(r.text, "html.parser")
    # Items found in the search are in the list_mode_thumb -div
    itemlist = soup.find("div", class_="list_mode_thumb").find_all("a", "item_row_flex")
    # Just respond with a link to the latest posting
    response = str(itemlist[0]["href"])
    sendMessage({"text": response.encode("utf8"), "chat_id": item["chat"]})


def showNew(item):
    print(item)
    # Fetch the items from Tori, soupify the results
    r = requests.get("https://www.tori.fi/koko_suomi?q={}".format(item["searchQuery"]))
    soup = BeautifulSoup(r.text, "html.parser")
    # Items found in the search are in the list_mode_thumb -div
    itemlist = soup.find("div", class_="list_mode_thumb").find_all("a", "item_row_flex")
    # This isn't pretty but it works :)
    # Init some values used in comparisons
    newItem = True
    newItemCount = 0
    # Build the base response
    response = "{} ({}):\n".format(stringlibrary.NEW_ITEM, item["searchQuery"])
    # Loop through all the items in the retrieved items...
    for n in itemlist:
        # If we haven't seen the item that is marked as the latest returned in the database...
        if newItem:
            print("{}:{}".format(n["id"], item["latest"]))
            # If the result of the search is already returned to the user, wrap things up
            if n["id"] == item["latest"]:
                newItem = False
            # If the result hasn't been shown to the user, add it to the response
            else:
                response += "{}\n".format(n["href"])
                newItemCount += 1

    # If no new items were found, don't bother talking to the user
    if newItemCount == 0:
        print("No new items for this search")
    # If new results were found, send them to the user
    else:
        table.update_item(
            Key={"id": item["id"]},
            UpdateExpression="SET latest = :latest",
            ExpressionAttributeValues={":latest": itemlist[0]["id"]},
        )
        sendMessage({"text": response.encode("utf8"), "chat_id": item["chat"]})


# Handles bot message sending, must include text and chat_id JSON entries
def sendMessage(data):
    url = BASE_URL + "/sendMessage"
    requests.post(url, data)
