# Copyright (c) 2020 Cisco and/or its affiliates.
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

#For SSO/CI sites, you can retrieve a personal access token 
# via: https://developer.webex.com/docs/api/getting-started
# For non-SSO/CI sites, provide a password
# If both are provided, the sample will attempt to use the access token

# (Common) Modify the below credentials to match your Webex Meeting site, host Webex ID and password

# host webex ID,sitename 

username = ""
password = None

# Example: For cisco.webex.com sitename will be cisco

sitename= "cisco"


# choose password for your scheduled meetings/trainings

meeting_password = "C!sco123"

# SECTION BELOW ONLY SSO/CI USERS - ignore if you already provided username and password

# (oauth2.py) Credentials for use with Webex SSO/CI OAuth sites. Only use this method if your account uses SSO

client_id=""
client_secret=""

# Once the OAth proccess is done sucessfully. The script will generate an access token 
access_token = ""