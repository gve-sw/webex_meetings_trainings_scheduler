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

import functions
import credentials
import csv
import datetime
import xml.etree.ElementTree as ET
import pandas as pd
from shutil import copyfile


if __name__ == "__main__":

    # AuthenticateUser and get sesssionTicket
    try:
        functions.sessionSecurityContext = functions.AuthenticateUser(
            credentials.sitename,
            credentials.username,
            credentials.password,
            credentials.access_token
        )

    # If an error occurs, print the error details and exit the script
    except functions.SendRequestError as err:
        print(err)
        raise SystemExit

    print("Authentication Accepted")
    print()
    print('Session Ticket:', '\n')
    print(functions.sessionSecurityContext['sessionTicket'])
    print()

    # Wait for the user to press Enter
    input('Press Enter to continue...')

    # GetSite - this will allow us to determine which meeting types are
    # supported by the user's site.  Then we'll parse/save the first type.

    try:
        response = functions.GetUser(functions.sessionSecurityContext)

    except functions.SendRequestError as err:
        print(err)
        raise SystemExit

    meetingType = response.find('{*}body/{*}bodyContent/{*}meetingTypes')[0].text
    
    #print()
    #print(f'First meetingType available: {meetingType}')
    #print()

    print('Now going to read csv file')
    input('Press Enter to continue...')

    # try to read csv file, if not, read an excel file and convert it to csv

    try:
        with open('meetings.csv','r') as csv_file:
            copyfile("meetings.csv", "schedule.csv")


    except:
        read_file = pd.read_excel(r'meetings.xlsx')
        read_file.to_csv(r'schedule.csv', index = None, header=True)

    with open('schedule.csv','r') as csv_file:
        csv_reader = csv.reader(csv_file)
        header = None

        for row_number, row in enumerate(csv_reader):

            if row_number is 0:
                header = row
                continue

            else:
                meeting_name = row[0]
                host = row[1]
                session_type = row[2]
                meeting_template = row[3]
                start_time = row[4]
                end_time = row[5]
                duration = row[6]

                attendees = row[7]
                attendees = attendees.replace(' ','')
                attendees = attendees.split(';')

                date = row[8]
                day_number = row[9]
                period_number = row[10]
                period_name = row[11]

                # Here we are swapping the date format from DD/MM/YYYY to MM/DD/YYYY 

                start_time = list(start_time)
                start_time[0:2] ,start_time[3:5] = start_time[3:5],start_time[0:2]
                start_time = ''.join(start_time)
                start_time = start_time + ":00"

                if session_type is 'M':

                    try:
                        response = functions.CreateMeeting(functions.sessionSecurityContext,
                            meetingPassword = credentials.meeting_password,
                            confName = meeting_name,
                            meetingType = meetingType,
                            agenda = period_name,
                            startDate = start_time,
                            duration = duration,
                            host = host,
                            attendees = attendees)

                        print('Meeting Key:', response.find('{*}body/{*}bodyContent/{*}meetingkey').text)

                    except functions.SendRequestError as err:
                        print(err)
                        raise SystemExit
                elif session_type is 'T':
                    try:
                        response = functions.CreateTraining(functions.sessionSecurityContext,
                            meetingPassword = credentials.meeting_password,
                            confName = meeting_name,
                            meetingType = meetingType,
                            agenda = period_name,
                            startDate = start_time,
                            duration = duration,
                            host = host,
                            attendees = attendees)
                        
                        print('Session Key:', response.find('{*}body/{*}bodyContent/{*}sessionkey').text)

                    except functions.SendRequestError as err:
                        print(err)
                        raise SystemExit

                print()
                print('Meeting Created for row ',row_number, '\n')
                print()

                input('Press Enter to continue...')
                continue
                
                # code ends here, below shows how some additional functions may be used 

                # LstsummaryMeeting for all upcoming meetings for the user
                try:
                    response = functions.LstsummaryMeeting(functions.sessionSecurityContext,
                        maximumNum = 10,
                        orderBy = 'STARTTIME',
                        orderAD = 'ASC',
                        hostWebExId = credentials.username,
                        startDateStart = datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S') )

                except functions.SendRequestError as err:
                    print(err)
                    raise SystemExit

                print( )
                print( 'Upcoming Meetings:', '\n')

                print( '{0:22}{1:25}{2:25}'.format( 'Start Time', 'Meeting Name', 'Meeting Key' ) )
                print( '{0:22}{1:25}{2:25}'.format( '-' * 10, '-' * 12, '-' * 11 ) )

                nextMeetingKey = response.find( '{*}body/{*}bodyContent/{*}meeting/{*}meetingKey').text

                for meeting in response.iter( '{*}meeting' ):

                    print( '{0:22}{1:25}{2:25}'.format( meeting.find( '{*}startDate' ).text,
                        meeting.find('{*}confName').text,
                        meeting.find('{*}meetingKey').text ))

                print( )
                input( 'Press Enter to continue...' )

                try:
                    response = functions.GetMeeting(functions.sessionSecurityContext,nextMeetingKey)
                except functions.SendRequestError as err:
                    print(err)
                    raise SystemError

                print( )
                print( 'Next Meeting Details:', '\n')
                print( '    Meeting Name:', response.find( '{*}body/{*}bodyContent/{*}metaData/{*}confName').text )
                print( '       Host Key:', response.find( '{*}body/{*}bodyContent/{*}hostKey').text )    
                print( '     Meeting Key:', response.find( '{*}body/{*}bodyContent/{*}meetingkey').text )    
                print( '      Start Time:', response.find( '{*}body/{*}bodyContent/{*}schedule/{*}startDate').text )    
                print( '       Join Link:', response.find( '{*}body/{*}bodyContent/{*}meetingLink').text )    
                print( '        Password:', response.find( '{*}body/{*}bodyContent/{*}accessControl/{*}meetingPassword').text )    

                print( )
                input( 'Press Enter to continue...' )

                try:
                    response = functions.DelMeeting(functions.sessionSecurityContext,nextMeetingKey)
                except functions.SendRequestError as err:
                    print(err)
                    raise SystemError    

                print( )
                print( 'Next Meeting Delete: SUCCESS', '\n')