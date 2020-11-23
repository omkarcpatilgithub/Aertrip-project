import dateparser
# import tensorflow.compat.v1 as tf
# tf.disable_v2_behavior()

from named_entity_recognition import Parser
import datetime
def next_day(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)

#### To convert generic time eg. morining: '06:00 - 12:00'
time_of_day = {'morning': '06:00 - 12:00'
               ,'afternoon': '12:00 - 06:00'
               ,'noon':'11:00 - 13:00'
               ,'evening':'18:00 - 24:00'
               ,'eve': '18:00 - 24:00'
               ,'night':'20:00 - 24:00'
               }
## weekday dictionary
weekday_dict = { "monday": 0
                 ,"tuesday": 1
                 ,"wednesday": 2
                 ,"thurday": 3
                 ,"friday": 4
                 ,"saturday": 5
                 ,"sunday": 6
                 }

#### to get special relative event's  dates
relative_date = {"deewali": datetime.date(2021, 11, 4)
                ,"diwali": datetime.date(2021, 11, 4)
                ,"christmas": datetime.date(2020, 12, 25)
                ,"holi": datetime.date(2021, 3, 28)
                ,"valentine": datetime.date(2021, 2, 14)
                ,"valentine's": datetime.date(2021, 2, 14)}




### Load the model
# p = Parser()
# # print("MODEL LOADING...")
# p.load_models("models/",allow_pickle=True)
# print("MODEL LOADED")
# print("PREDICTING...")


def pred(sent):
    p = Parser()
    p.load_models("models/", allow_pickle=True)
    return_flag = False
    pred = p.predict(sent)
    print(pred)

    from_city = ''
    to_city = ''
    departure_date = ''
    return_date = ''
    departure_time = ''
    return_time = ''
    t_relative_date = ''

    ### extract data from tags
    for i in pred:
        if (i[1] == 'F-CITY'):
            from_city = i[0]
        elif (i[1] == 'T-CITY'):
            to_city = i[0]
        elif (i[1] == 'G-TIME'):
            # departure_date = dateparser.parse(i[0]).strftime("%m/%d/%Y")
            departure_date = departure_date + i[0] + ' '
        elif (i[1] == 'R-TIME'):
            # return_date = dateparser.parse(i[0]).strftime("%m/%d/%Y")
            return_date = return_date + i[0] + ' '
        elif (i[1] == 'IG-TIME'):
            departure_time = departure_time + time_of_day.get(i[0].lower(), i[0]) + ' '
        elif (i[1] == 'IR-TIME'):
            return_time = return_time + time_of_day.get(i[0].lower(), i[0]) + ' '
        elif (i[1] == 'RET'):
            return_flag = True
        elif (i[1] == 'T-REL-DATE'):
            t_relative_date = i[0]

    ## if relative date and monday (G-TIME) is present and g time exist in days dictionary
    # then get date after the relative date

    # if relative date exist and no G time then     departure is relative date

    if (t_relative_date and t_relative_date.lower() in relative_date):
        if (departure_date):
            if (
                    departure_date.strip().lower() in weekday_dict):  ## relative day exist and departure is said to be on monday,tues....

                rel_day = relative_date.get(t_relative_date.lower(), t_relative_date)
                coming_day = weekday_dict[departure_date.strip().lower()]
                departure_date = next_day(rel_day, coming_day)

            else:  ## relative day exist but date is in 7th may kind date (rare case)

                departure_date = dateparser.parse(departure_date,settings={'PREFER_DATES_FROM': 'future'}).strftime("%m/%d/%Y")
        else:  ## relative date is present and departure date is not mentioned then set ralative date to departure

            departure_date = relative_date.get(t_relative_date.lower(), t_relative_date)

    # ### change departure date in required format for all the posibilities
    if (departure_date):
        departure_date = dateparser.parse(str(departure_date),settings={'PREFER_DATES_FROM': 'future'}).strftime("%m/%d/%Y")

    ### return date should always be after departure
    if (return_date):
        if (departure_date):
            if (return_date.strip().lower() in weekday_dict):
                rel_day = datetime.datetime.strptime(departure_date, '%m/%d/%Y')
                coming_day = weekday_dict[return_date.strip().lower()]
                return_date = next_day(rel_day, coming_day)

        ## change return date in required format for all the posibilities
        print(return_date)
        return_date = dateparser.parse(str(return_date),settings={'PREFER_DATES_FROM': 'future'}).strftime("%m/%d/%Y")

    ### change departure and return departure time in format
    time = dateparser.parse(departure_time,settings={'PREFER_DATES_FROM': 'future'})
    if (time):
        departure_time = time.strftime("%H:%M:%S")
    time = dateparser.parse(return_time,settings={'PREFER_DATES_FROM': 'future'})
    if (time):
        return_time = time.strftime("%H:%M:%S")

    ## Follow-up query if From and To city is not given
    if (from_city == ''):
        from_city = 'Blank (Follow-up query: "Could you please let me know from which city you want to start your journey?"'
    if (to_city == ''):
        to_city = 'Blank (Follow-up query: "Thank you Sir/Mam, Please tell me the destination of your journey while going?"'

    ### Detect intent
    print(sent)
    if (return_flag):
        intent = "Return Search"
    else:
        intent = "One Way search"

    ### Print all data
    print(intent)
    print()
    print("From: \t\t" + from_city)
    print("To: \t\t" + to_city)
    print("Onward: \t" + departure_date)
    print("Return: \t" + return_date)
    print("Onward Departure Time: \t" + departure_time)
    print("Return Departure Time: \t" + return_time)

    ## If we need to return extracted data in json format
    dict = {
        "intent": intent
        , "from": from_city
        , "to": to_city
        , "onward": departure_date
        , "return": return_date
        , "onward_departure_time": departure_time
        , "return departure time": return_time
    }

    return dict