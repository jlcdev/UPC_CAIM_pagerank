#!/usr/bin/python

from collections import namedtuple
import time
import sys

class Edge:
    def __init__ (self, origin=None):
        self.origin = origin # write appropriate value
        self.weight = ... # write appropriate value

    def __repr__(self):
        return "edge: {0} {1}".format(self.origin, self.weight)
        
    ## write rest of code that you need for this class

class Airport:
    def __init__ (self, iden=None, name=None):
        self.code = iden
        self.name = name
        self.routes = []
        self.routeHash = dict()
        self.outweight = 0  # write appropriate value
        self.pageIndex = ...

    def __repr__(self):
        return "{0}\t{2}\t{1}".format(self.code, self.name, self.outweight)

edgeList = [] # list of Edge
edgeHash = dict() # hash of edge to ease the match
airportList = [] # list of Airport
airportHash = dict() # hash key IATA code -> Airport

def readAirports(fd):
    print("Reading Airport file from {0}".format(fd))
    airportsTxt = open(fd, "r");
    cont = 0
    for line in airportsTxt.readlines():
        a = Airport()
        try:
            temp = line.split(',')
            if len(temp[4]) != 5 :
                raise Exception('not an IATA code')
            a.name=temp[1][1:-1] + ", " + temp[3][1:-1]
            a.code=temp[4][1:-1]
        except Exception as inst:
            pass
        else:
            cont += 1
            a.pageIndex = len(airportList)
            airportList.append(a)
            airportHash[a.code] = a
    airportsTxt.close()
    print("There were {0} Airports with IATA code".format(cont))

def readRoutes(fd):
    print("Reading Routes file from {0}".format(fd))
    routesTxt = open(fd, "r");
    cont = 0
    for line in routesTxt.readlines():
        e = Edge()
        try:
            temp = line.split(',')
            if len(temp[2]) != 3 or len(temp[4]) != 3:
                raise Exception('not an IATA code')
            dest = temp[4]
            origin = temp[2]
            if not (origin in airportHash and dest in airportHash):
                raise Exception('not valid Airport')
            e.origin = origin
            e.weight = 1
        except Exception as inst:
            pass
        else:
            cont += 1
            if dest in airportHash:
                if not e.origin in airportHash[dest].routeHash:
                    airportHash[dest].routes.append(e)
                    airportHash[dest].routeHash[e.origin] = e
                else:
                    airportHash[dest].routeHash[e.origin].weight += 1
                if e.origin in airportHash:
                    airportHash[e.origin].outweight += 1
    print("There were {0} Routes with IATA code".format(cont))

def stoppingCondition(old,new,n_decimals):
    return ([round(o,n_decimals) for o in old] == [round(n,n_decimals) for n in new])

def computePageRanks():
    n = len(airportList)
    P = [1.0/n] * n
    last_P = [0] * n
    L = 0.85
    n_decimals = 8
    it = 0

    ini_weight = 0
    for i in range(n):
        if airportList[i].outweight == 0:
            ini_weight += P[i]/n

    while not stoppingCondition(last_P,P,n_decimals):
        last_P = P
        Q = [0] * n;
        end_weight = 0
        for i in range(n):
            dest = airportList[i]
            origins = dest.routes
            sum_res = ini_weight
            for route in origins:
                j = airportHash[route.origin].pageIndex
                sum_res += P[j]*route.weight/airportList[j].outweight
            Q[i] = L * sum_res + (1.0-L)/n

            if airportList[i].outweight == 0:
                end_weight += Q[i]/n

        ini_weight = end_weight
        P = Q
        it += 1
    return it,P

def outputPageRanks(pageRanks):
    airportList.sort(key=lambda ax: pageRanks[ax.pageIndex], reverse=True)
    for a in airportList:
        #print('PR: %0.16f | Airport: [%s] %s' % (pageRanks[a.pageIndex],a.code,a.name))
        print('Airport: [%s] %s' % (a.code,a.name))

def main(argv=None):
    readAirports("airports.txt")
    readRoutes("routes.txt")
    time1 = time.time()
    iterations, pageRanks = computePageRanks()
    time2 = time.time()
    outputPageRanks(pageRanks)
    print("#Iterations:", iterations)
    print("Time of computePageRanks():", time2-time1)


if __name__ == "__main__":
    sys.exit(main())
