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

import requests
import datetime
from lxml import etree
import credentials
import xml.etree.ElementTree as ET

# Change to true to enable request/response debug output
DEBUG = False

# Once the user is authenticated, the sessionTicket for all API requests will be stored here
sessionSecurityContext = { }

# Custom exception for errors when sending requests
class SendRequestError(Exception):

    def __init__(self, result, reason):
        self.result = result
        self.reason = reason

    pass

# Generic function for sending XML API requests
#   envelope : the full XML content of the request
def sendRequest(envelope):

    if DEBUG:
        print( envelope )

    # Use the requests library to POST the XML envelope to the Webex API endpoint
    headers = { 'Content-Type': 'application/xml'}
    response = requests.post( 'https://api.webex.com/WBXService/XMLService', envelope )

    # Check for HTTP errors
    try: 
        response.raise_for_status()
    except requests.exceptions.HTTPError as err: 
        raise SendRequestError( 'HTTP ' + str(response.status_code), response.content.decode("utf-8") )

    # Use the lxml ElementTree object to parse the response XML
    message = etree.fromstring( response.content )

    if DEBUG:
        print( etree.tostring( message, pretty_print = True, encoding = 'unicode' ) )   

    # Use the find() method with an XPath to get the 'result' element's text
    # Note: {*} is pre-pended to each element name - ignores namespaces
    # If not SUCCESS...
    if message.find( '{*}header/{*}response/{*}result').text != 'SUCCESS':

        result = message.find( '{*}header/{*}response/{*}result').text
        reason = message.find( '{*}header/{*}response/{*}reason').text

        #...raise an exception containing the result and reason element content
        raise SendRequestError( result, reason )

    return message

def AuthenticateUser(siteName, webExId, password, accessToken):

    # If an access token is provided in .env, we'll use this form
    if ( accessToken ):
        request = f'''<?xml version="1.0" encoding="UTF-8"?>
            <serv:message xmlns:serv="http://www.webex.com/schemas/2002/06/service"
                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                <header>
                    <securityContext>
                        <siteName>{siteName}</siteName>
                        <webExID>{webExId}</webExID>
                    </securityContext>
                </header>
                <body>
                    <bodyContent xsi:type="java:com.webex.service.binding.user.AuthenticateUser">
                        <accessToken>{accessToken}</accessToken>
                    </bodyContent>
                </body>
            </serv:message>'''
    else:
        # If no access token, assume a password was provided, using this form
        request = f'''<?xml version="1.0" encoding="UTF-8"?>
            <serv:message xmlns:serv="http://www.webex.com/schemas/2002/06/service"
                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                <header>
                    <securityContext>
                        <siteName>{siteName}</siteName>
                        <webExID>{webExId}</webExID>
                        <password>{password}</password>
                    </securityContext>
                </header>
                <body>
                    <bodyContent xsi:type="java:com.webex.service.binding.user.AuthenticateUser"/>
                </body>
            </serv:message>'''

    # Make the API request
    response = sendRequest(request)

    # Return an object containing the security context info with sessionTicket
    return {
            'siteName': siteName,
            'webExId': webExId,
            'sessionTicket': response.find( '{*}body/{*}bodyContent/{*}sessionTicket' ).text
            }

def GetUser(sessionSecurityContext):

    request = f'''<?xml version="1.0" encoding="UTF-8"?>
        <serv:message xmlns:serv="http://www.webex.com/schemas/2002/06/service"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <header>
                <securityContext>
                    <siteName>{sessionSecurityContext['siteName']}</siteName>
                    <webExID>{sessionSecurityContext['webExId']}</webExID>
                    <sessionTicket>{sessionSecurityContext['sessionTicket']}</sessionTicket>
                </securityContext>
            </header>
            <body>
                <bodyContent xsi:type="java:com.webex.service.binding.user.GetUser">
                    <webExId>{sessionSecurityContext['webExId']}</webExId>
                </bodyContent>
            </body>
        </serv:message>'''

    # Make the API request
    response = sendRequest( request )

    # Return an object containing the response
    return response

def CreateTraining(sessionSecurityContext,
                   meetingPassword,
                   confName,
                   meetingType,
                   agenda,
                   startDate,
                   duration,
                   host,
                   attendees):
                   
    request = f'''<?xml version="1.0" encoding="UTF-8"?>
            <serv:message xmlns:serv="http://www.webex.com/schemas/2002/06/service"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <header>
                <securityContext>
                    <siteName>{sessionSecurityContext["siteName"]}</siteName>
                    <webExID>{sessionSecurityContext["webExId"]}</webExID>
                    <sessionTicket>{sessionSecurityContext["sessionTicket"]}</sessionTicket>
                </securityContext>
            </header>
            <body>
                <bodyContent xsi:type=
                    "java:com.webex.service.binding.training.CreateTrainingSession">
                    <accessControl>
                        <listing>UNLISTED</listing>
                        <sessionPassword>C1sco123</sessionPassword>
                    </accessControl>
                    <schedule>
                        <startDate>{startDate}</startDate>
                        <duration>{duration}</duration>
                        <joinTeleconfBeforeHost>false</joinTeleconfBeforeHost>
                    </schedule>
                    <metaData>
                        <confName>{confName}</confName>
                        <agenda>{agenda}</agenda>
                    </metaData>
                    <enableOptions>
                        <attendeeList>false</attendeeList>
                        <javaClient>false</javaClient>
                        <nativeClient>true</nativeClient>
                        <chat>false</chat>
                        <poll>false</poll>
                        <audioVideo>false</audioVideo>
                        <fileShare>false</fileShare>
                        <presentation>false</presentation>
                        <applicationShare>false</applicationShare>
                        <desktopShare>false</desktopShare>
                        <webTour>false</webTour>
                        <trainingSessionRecord>false</trainingSessionRecord>
                        <annotation>false</annotation>
                        <importDocument>false</importDocument>
                        <saveDocument>false</saveDocument>
                        <printDocument>false</printDocument>
                        <pointer>false</pointer>
                        <switchPage>false</switchPage>
                        <fullScreen>false</fullScreen>
                        <thumbnail>false</thumbnail>
                        <zoom>false</zoom>
                        <copyPage>false</copyPage>
                        <rcAppShare>false</rcAppShare>
                        <rcDesktopShare>false</rcDesktopShare>
                        <rcWebTour>false</rcWebTour>
                        <attendeeRecordTrainingSession>false
                        </attendeeRecordTrainingSession>
                        <voip>false</voip>
                        <faxIntoTrainingSession>false</faxIntoTrainingSession>
                        <autoDeleteAfterMeetingEnd>true</autoDeleteAfterMeetingEnd>
                    </enableOptions>
                    <telephony>
                        <telephonySupport>NONE</telephonySupport>
                        <numPhoneLines>4</numPhoneLines>
                        <extTelephonyURL>String</extTelephonyURL>
                        <extTelephonyDescription>String</extTelephonyDescription>
                        <enableTSP>false</enableTSP>
                        <tspAccountIndex>1</tspAccountIndex>
                    </telephony>
                    <tracking>
                        <trackingCode1>trackingCode1</trackingCode1>
                        <trackingCode2>trackingCode2</trackingCode2>
                        <trackingCode3>trackingCode3</trackingCode3>
                        <trackingCode4>trackingCode4</trackingCode4>
                        <trackingCode5>trackingCode5</trackingCode5>
                        <trackingCode6>trackingCode6</trackingCode6>
                        <trackingCode7>trackingCode7</trackingCode7>
                        <trackingCode8>trackingCode8</trackingCode8>
                        <trackingCode9>trackingCode9</trackingCode9>
                        <trackingCode10>trackingCode10</trackingCode10>
                    </tracking>
                    <remind>
                        <enableReminder>True</enableReminder>
                        <emails>
                            <email>test@mail.com</email>
                        </emails>
                        <sendEmail>True</sendEmail>
                        <mobile>String</mobile>
                        <sendMobile>false</sendMobile>
                        <daysAhead>1</daysAhead>
                        <hoursAhead>1</hoursAhead>
                        <minutesAhead>1</minutesAhead>
                    </remind>
                    <presenters>
                        <participants>
                            <participant>
                                <person>
                                    <name>{host}</name>
                                    <email>{host}</email>
                                    <type>MEMBER</type>
                                </person>
                                <role>HOST</role>
                            </participant>
                        </participants>
                    </presenters>
                   <attendees>
                        <participants>
                        </participants>
                    </attendees>
                    <attendeeOptions>
                        <emailInvitations>true</emailInvitations>
                    </attendeeOptions>
                </bodyContent>
            </body>
        </serv:message> '''


    # here we are reading the request xml string and appending the attendees by emails

    tree = ET.fromstring(request)
    root = ET.fromstring(request)
    body = root[1][0][9][0]

    for address in attendees:

        participant = ET.SubElement(body, "participant")
        person = ET.SubElement(participant, "person")
        name = ET.SubElement(person, "name")
        email = ET.SubElement(person, "email")
        #member = ET.SubElement(person, "type")
        #role = ET.SubElement(participant,'role')

        #role.text = "MEMBER"
        name.text = address
        email.text= address
        #member.text = "MEMBER"
        request = ET.tostring(root)
        
    response = sendRequest(request)

    return response

def CreateMeeting(sessionSecurityContext,
                   meetingPassword,
                   confName,
                   meetingType,
                   agenda,
                   startDate,
                   duration,
                   host,
                   attendees
                    ):

    #remove the domain from host email
    host = host.split("@")[0]

    request = f'''<?xml version="1.0" encoding="UTF-8"?>
        <serv:message xmlns:serv="http://www.webex.com/schemas/2002/06/service"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <header>
                <securityContext>
                    <siteName>{sessionSecurityContext["siteName"]}</siteName>
                    <webExID>{sessionSecurityContext["webExId"]}</webExID>
                    <sessionTicket>{sessionSecurityContext["sessionTicket"]}</sessionTicket>  
                </securityContext>
            </header>
            <body>
                <bodyContent
                    xsi:type="java:com.webex.service.binding.meeting.CreateMeeting">
                    <accessControl>
                        <meetingPassword>{meetingPassword}</meetingPassword>
                    </accessControl>
                    <metaData>
                        <confName>{confName}</confName>
                        <agenda>{agenda}</agenda>
                    </metaData>
                    <participants>
                        <attendees>
                        </attendees>
                    </participants>
                    <enableOptions>
                        <chat>true</chat>
                        <poll>true</poll>
                        <audioVideo>true</audioVideo>
                        <supportE2E>TRUE</supportE2E>
                        <autoRecord>TRUE</autoRecord>
                    </enableOptions>
                    <schedule>
                        <startDate>{startDate}</startDate>
                        <openTime>900</openTime>
                        <joinTeleconfBeforeHost>false</joinTeleconfBeforeHost>
                        <duration>{duration}</duration>
                        <hostWebExID>{host}</hostWebExID>
                    </schedule>
                    <telephony>
                        <telephonySupport>CALLIN</telephonySupport>
                        <extTelephonyDescription>
                            Call 1-800-555-1234, Passcode 98765
                        </extTelephonyDescription>
                    </telephony>
                    <remind>
            	        <enableReminder>True</enableReminder>
            	        <sendEmail>True</sendEmail>
                    </remind>
                    <attendeeOptions>
            	        <emailInvitations>True</emailInvitations>
                    </attendeeOptions>
                </bodyContent>
            </body>
        </serv:message>''' 

    # here we are reading the request xml string and appending the attendees by emails
    
    tree = ET.ElementTree(ET.fromstring(request))

    for address in attendees:
        root = tree.getroot()
        body = root[1][0][2][0]

       
        tree = ET.ElementTree(ET.fromstring(request))
        root = tree.getroot()
        body = root[1][0][2][0]
        attendee = ET.SubElement(body, "attendee")
        person = ET.SubElement(attendee, "person")
        name = ET.SubElement(person, "name")
        email = ET.SubElement(person, "email")

        name.text = address
        email.text= address
        request = ET.tostring(root)

    response = sendRequest(request)

    return response

def LstsummaryMeeting(sessionSecurityContext,
    maximumNum,
    orderBy,
    orderAD,
    hostWebExId,
    startDateStart ):

    request = f'''<?xml version="1.0" encoding="UTF-8"?>
        <serv:message xmlns:serv="http://www.webex.com/schemas/2002/06/service"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <header>
                <securityContext>
                    <siteName>{sessionSecurityContext["siteName"]}</siteName>
                    <webExID>{sessionSecurityContext["webExId"]}</webExID>
                    <sessionTicket>{sessionSecurityContext["sessionTicket"]}</sessionTicket>  
                </securityContext>
            </header>
            <body>
                <bodyContent xsi:type="java:com.webex.service.binding.meeting.LstsummaryMeeting">
                    <listControl>
                        <maximumNum>{maximumNum}</maximumNum>
                        <listMethod>AND</listMethod>
                    </listControl>
                    <order>
                        <orderBy>{orderBy}</orderBy>
                        <orderAD>{orderAD}</orderAD>
                    </order>
                    <dateScope>
                        <startDateStart>{startDateStart}</startDateStart>
                        <timeZoneID>4</timeZoneID>
                    </dateScope>
                    <hostWebExID>{hostWebExId}</hostWebExID>
                </bodyContent>
            </body>
        </serv:message>'''

    response = sendRequest( request )

    return response

def GetMeeting(sessionSecurityContext, meetingKey):

    request = f'''<?xml version="1.0" encoding="ISO-8859-1"?>
        <serv:message
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xmlns:serv="http://www.webex.com/schemas/2002/06/service">
            <header>
                <securityContext>
                    <siteName>{sessionSecurityContext["siteName"]}</siteName>
                    <webExID>{sessionSecurityContext["webExId"]}</webExID>
                    <sessionTicket>{sessionSecurityContext["sessionTicket"]}</sessionTicket>  
                </securityContext>
            </header>
            <body>
                <bodyContent xsi:type="java:com.webex.service.binding.meeting.GetMeeting">
                    <meetingKey>{meetingKey}</meetingKey>
                </bodyContent>
            </body>
        </serv:message>'''

    response = sendRequest( request )

    return response

def DelMeeting(sessionSecurityContext, meetingKey):

    request = f'''<?xml version="1.0" encoding="ISO-8859-1"?>
        <serv:message
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xmlns:serv="http://www.webex.com/schemas/2002/06/service">
            <header>
                <securityContext>
                    <siteName>{sessionSecurityContext["siteName"]}</siteName>
                    <webExID>{sessionSecurityContext["webExId"]}</webExID>
                    <sessionTicket>{sessionSecurityContext["sessionTicket"]}</sessionTicket>  
                </securityContext>
            </header>
            <body>
            <bodyContent xsi:type="java:com.webex.service.binding.meeting.DelMeeting">
                <meetingKey>{meetingKey}</meetingKey>
            </bodyContent>
            </body>
        </serv:message>'''

    response = sendRequest( request )

    return response
