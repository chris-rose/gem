import pandas as pd
import networkx as nx
from sqlalchemy import create_engine, select

# canonical schedule = (
# (route_entry_1, origin_1, departure_1, destination_1, arrival_1),
# ...
# (route_entry_n, origin_n, departure_n, destination_n, arrival_n)
# )

# Some of these function are both defined in __init__ and operational modules (transit.py) This is for the sake
# of clarity and ease of use.  The functions defined here establish default values for arguments in the transit.py file.
# Those same arguments need to be in the transit namesapce so users have the option of creating novel schedules and amending
# digraphs manually without calling a different submodule (Users should only need to import gem.transit, not gem.transit and 
# gem)

def getElapsed(past, future):
    
    '''Accept a time in the past (Minutes from midnight on Monday) and the future, return the time
    elapsed between them.'''
    
    if past <= future:
        return future - past
    else:
        return (future - past) + (7*24*60)


def convertToGraph(schedule):
    
    '''Accepts a schedule to be converted to a graph.  Every row in the schedule can be interpreted as a decision 
      (not a point).  Draw an edge between the destination of a previous decision (predecessor) and the
       origins of every succesive decision (successors) for every predecessor.'''
    
    graph = nx.DiGraph()
    for predecessor in schedule:
        for successor in getSubSchedule(predecessor[3], schedule):
            
            weight = ((predecessor[4], successor[2]), (successor[2], successor[4]))
            weight = sum([getElapsed(w[0], w[1]) for w in weight]) # Time between predecessor and successor
            graph.add_edge(predecessor, successor, weight=weight)
    
    return graph

def getSubSchedule(point, schedule, point_context='origin'):
    
    '''Accepts a point, the schedule, and the context of the point(either 'origin' or 'destination'). Returns either the 'origin' or 'destination' point.'''
    
    if point_context == 'origin':
        return [t for t in schedule if t[1] == point]
    elif point_context == 'destination':
        return [t for t in schedule if t[3] == point]


def default():
    
    '''Method used to setup default database connection. Returns the default zip codes, schedule, and digraph.'''

    # engine=create_engine('postgresql://dataowner:dataowner@xxxxxx:xxxx/xxxxxxx')
    
    # default_schedule = pd.read_sql_table('concurrent_schedule', con=engine) # concurrent schedule
    
    default_schedule = pd.DataFrame({'ROUTE':['A', 'H', 'B', 'C', 'D', 'E', 'F', 'G'],
                         'A/P CITY':['Los Angeles', 'Chicago', 'Los Angeles', 'Chicago', 'Saint Louis', 'Memphis', 'Saint Louis', 'Boston'],
                         'DEPARTURE':[500, 4700, 5000, 9000, 3000, 200, 1000, 500],
                         'A/P DST': ['Chicago', 'Saint Louis', 'Chicago', 'Saint Louis', 'Memphis', 'Boston', 'Miami', 'Chicago'],
                         'ARRIVAL': [4600, 8000, 10000, 200, 6000, 2100, 3000, 2700],})
    
    default_schedule = default_schedule[['ROUTE', 'A/P CITY', 'DEPARTURE', 'A/P DST', 'ARRIVAL']]
    default_schedule = (tuple(x) for x in default_schedule.values)
    default_schedule = [row for row in default_schedule]
    default_digraph = convertToGraph(default_schedule)
    
    # express_zipcodes = pd.read_sql_query("SELECT * FROM express_masterlist", con=engine)
    # express_zipcodes = express_zipcodes.set_index('pcmiler_zip')
    
    # return express_zipcodes, default_schedule, default_digraph
    return default_schedule, default_digraph

