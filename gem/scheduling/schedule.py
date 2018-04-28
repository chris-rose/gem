from sqlalchemy import create_engine, select
import pandas as pd

engine=create_engine('postgresql://dataowner:dataowner@devd512a:5432/sandbox')

def getMinutes(t):
    
    '''Accepts either a possible military time or possible day of the week and validates.  Returns the military time or an error 
    message notifying the user of incorrect input.'''
    
    isodays = {'MON': 0, 'TUE': 1, 'WED': 2, 'THU': 3,'FRI': 4, 'SAT': 5, 'SUN': 6}
    if len(t) == 4 and t.isdigit(): # if military time
        return int(t[0:2]) * 60 + int(t[2:4])
    elif t in isodays.keys(): # if day of the week
        return isodays[t] * 24 * 60
    else:
        return 'input not a day, or a military time'

class Parsing():
    
    '''Class of functions that handle parsing and sorting operational data; every function should return a
    canonical schedule object.'''
    
    def read_operations_excel(file_path):
        
        '''Accepts a file and parses data.  Returns the created subframe.'''
        
        relevant_columns = ['ROUTE', 'A/P CITY', 'ETD', 'ETA/SO', 'ADAY', 'A/P DST', 'DDAY']
        df_unmolested = pd.read_excel(file_path)
        df = pd.read_excel(file_path, usecols=relevant_columns,
             converters={col: lambda x: str(x).strip() for col in relevant_columns})
        df = df.dropna().reset_index(drop=True)
        df['DEPARTURE'] = df['DDAY'].apply(getMinutes) + df['ETD'].apply(getMinutes) 
        df['ARRIVAL'] = df['ADAY'].apply(getMinutes) + df['ETA/SO'].apply(getMinutes) 
        subframe = df[['ROUTE', 'A/P CITY', 'DEPARTURE', 'A/P DST', 'ARRIVAL']]
        return subframe
        #schedule = (tuple(x) for x in subframe.values)
        #return schedule
    
    def read_other_format():
        
        pass

#df=Parsing.read_operations_excel(file_path)
#df.to_sql('concurrent_schedule', con=engine)





