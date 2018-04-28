import itertools
import gem
from copy import deepcopy
import networkx as nx

default_schedule, default_digraph = gem.default()

def getElapsed(past, future):
    
    '''Accept a time in the past (Minutes from midnight on Monday) and the future, return the time
       elapsed between them.'''
    
    if past <= future:
        return future - past
    else:
        return (future - past) + (7*24*60)


def getSubSchedule(point, schedule, point_context='origin'):
    
    '''Accepts a point, the schedule, and the context of the point(either 'origin' or 'destination'). Returns either the
      'origin' or 'destination' sub schedule.'''
    
    if point_context == 'origin':
        return [t for t in schedule if t[1] == point] # Section of passed schedule where the passed point was an origin
    elif point_context == 'destination':
        return [t for t in schedule if t[3] == point] # Section of passed schedule where the passed point was a destination

    
def augmentDigraph(digraph, origin, destination, time):
    
    '''Accepts a digraph, an origin, a destination, and a time, attaches the origin and destination nodes
       to the digraph for use in queries.'''
    
    for succsessor in getSubSchedule(origin, digraph.nodes()):
        weight = getElapsed(time, succsessor[2]) + getElapsed(succsessor[2], succsessor[4])  # Time after pickup
        digraph.add_edge('Origin', succsessor, weight=weight)
        
    for predecessor in getSubSchedule(destination, digraph.nodes(), point_context='destination'):
        digraph.add_edge(predecessor, 'Destination', weight=0) # Placeholder for section band delivery time



def validate_point(digraph, point):
    
    '''Accepts a digraph and a point to validate.  Raises the appropriate exception if the point is invalid or returns the 
       point if it is valid.'''
    
    exception_general = 'is neither a 5 digit ZIP Code, nor a location used on the route schedule'
    exception_masterlist = 'not in express masterlist'
    exception_digraph = 'not in the Network Digraph'
    exception_zipcode_association = ('You passed a valid zipcode, but the route schedule does not'
                                    'use airport codes.  Try querying the graph with native input.')
    
    valid_locations = list([node[1] for node in digraph.nodes()])
    valid_locations.extend([node[3] for node in digraph.nodes()])# Every point recognized as an origin in the digraph
    
    if len(point) != 5 and point not in valid_locations: # Neither zipcode, not point in digraph
        
        raise Exception(point, exception_general)
    
    elif len(point) == 5: # Maybe zipcode?
        
        try:
            
            point = express_zipcodes['airport_code'][point] # Look for zip in master list
        
        except(KeyError):
            
            raise Exception(point, exception_masterlist) # If what looked like a zip not in masterlist, raise exception
        
        if point not in valid_locations:  # Point not in digraph
            
            raise Exception(exception_zipcode_association)
    
    else:
        
        if point not in valid_locations:
            
            raise Exception(point, exception_digraph)
    
    return point



def validate_time(time):
    
    '''Accepts time to be validated.  Raises an exception if invalid, returns time if valid.'''
    
    if time > 10080 or time < 0:
        raise Exception('Time must be minutes past midnight on Monday (0-10080 are valid)')
    return time



def traverseGraph(origin, destination, time, digraph=default_digraph, return_path=False):
    
    
    '''Accepts an origin, destination, time, digraph(default unless one is provided), and a return_path value.  If      
       return_path==True, returns the path and length(total elapsed time).  If return_path==False, returns just the length.'''
    
    D = deepcopy(digraph) # Make a copy to avoid stacking origin, destination nodes during augmentation
    
    # origin, destination = (validate_point(D, origin), validate_point(D, destination)) # validate arguments passed
    time = validate_time(time)
    
    if origin == destination:  # Local deliveries have trivial returns
        if return_path == True:
            return (['Origin', (origin), 'Destination'], 0)
        else:
            return 0
        
    
    
    augmentDigraph(D, origin, destination, time)
    length = nx.dijkstra_path_length(D, 'Origin', 'Destination') # get the length of the best path
    
    if return_path == True:
        path = nx.dijkstra_path(D, 'Origin', 'Destination')  # get the best path
        return path, length
    else:
        return length
    
def getTransitMatrix(digraph=default_digraph, load_time=360):
    
    '''Accepts a digraph(default unless provided) and a load time(defaulted at 360), creates a matrix with all possible 
       combinations of service area to service area for everyday of the week for the given time.  Returns the matrix(times).'''
    
    points = list(set([node[1] for node in digraph.nodes()]))
    times = []
    for c in itertools.product(points, points):
        for t in [360 + (60*24*i) for i in range(6)]:
            try:
                times.append((c[0], c[1], t, traverseGraph(c[0], c[1], t, digraph)))
            except Exception as e:
                times.append((c[0], c[1], t, e))
    return times






