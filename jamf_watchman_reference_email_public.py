#!/usr/local/bin/python3

import requests
import json
import subprocess


####
# Uses JAMF enviro variables to take the email address from the 
# computer name in jamf and puts into Watchman as the reference email. 
# Currently the 'username' in the computer -> location is used but can be changed
# 
# Written by Matt Jerome, IT Systems Administrator 11/22/2021
####

####
# variables
####
jamf_basic_auth = "$4"

watchman_bearer = "$5"

subdomain = "$6"

watchman_api = "$7"


####
# Functions
####

def email_address(data):
	try:
		email = data["userAndLocation"]["username"]
	except:
		email = "User Email Error"
	return email

def get_jamf_email(computer_name,subdomain,jamf_basic_auth):
	url = f"https://{subdomain}.jamfcloud.com/JSSResource/computers/name/{computer_name}"
	
	headers = {"Accept": "application/json",
	"Authorization": f"Basic {jamf_basic_auth}"}
	
	response = requests.request("GET", url, headers=headers)
	results = response.json()
	email = None
	try:
		email = results['computer']['location']['username']
	except:
		pass
	return email

def get_watchman_data(subdomain,watchman_api,watchman_bearer):
	url = f"https://{subdomain}.monitoringclient.com/v2.5/computers?page=1&api_key={watchman_api}"
	
	payload={}
	headers = {
	  'Authorization': f'Bearer {watchman_bearer}'
	}
	
	response = requests.request("GET", url, headers=headers, data=payload)
	results = response.json()
	return results
	

def insert_reference_email(email,id,subdomain,watchman_api):
	if email:
		url = f"https://{subdomain}.monitoringclient.com/v2.5/computers/{id}"
		headers = {
		'Content-Type': 'application/x-www-form-urlencoded'
		}
		data = {
		'api_key': f'{watchman_api}',
		'computer[reference_email]': email
		}
		response = requests.put(url, headers=headers, data=data)
	else:
		print("No valid Email")
		
		
		
####
# This is where stuff happens
####

hostname = subprocess.getoutput('hostname')
watchman_computer_data = get_watchman_data(subdomain, watchman_api,watchman_bearer)
for i in watchman_computer_data:
	if hostname not in i['computer_name']:
		continue # goes to next record
	else:
		print("Computer Record Located")
		watchman_id = i['watchman_id']
		print("Watchman ID assigned")
		reference_email = i['reference_email']
		email_address = get_jamf_email(hostname,subdomain,jamf_basic_auth)
		insert_reference_email(email_address, watchman_id,subdomain,watchman_api)
		print("Assignment complete.")
		break # exits loop completely 

	