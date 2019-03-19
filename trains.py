#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-12-20 15:40:03
# @Author  : Joseph
import base64
import datetime
import hashlib
import hmac
import json
import pdb



## Single route.
class SingleRoute(object):

    def __init__(self, fromStop, toStop, weight):
        self.fromStop = fromStop
        self.toStop = toStop
        self.weight = weight
        self.route = fromStop + toStop


## A single route container
class RouteSet(object):

    _routes = {}
    _exRouteIndex = {}

    ## @routeData
    def __init__(self, routeData):
        self._routes = {}
        self._exRouteIndex = {}
        for route, weight in routeData.items():
            ## check format
            if type(route) != str or len(route) != 2 or type(weight) != int:
                ## wrong format
                continue
            ## init single route
            self._routes[route] = SingleRoute(route[0], route[1], weight)
        ## build index
        self._build_route_index()

    def _build_route_index(self):
        self.fromStops = {}
        toStops = []

        for sRoute in self._routes.values():
            if sRoute.fromStop not in self.fromStops:
                self.fromStops[sRoute.fromStop] = [sRoute]
            else:
                self.fromStops[sRoute.fromStop].append(sRoute)
            if sRoute.toStop not in toStops:
                toStops.append(sRoute.toStop)
        ##
        for fromStop, routeList in self.fromStops.items():
            for toStop in toStops:
                #pdb.set_trace()
                routeChain = self._extend_route(fromStop, toStop, [])
                if len(routeChain) > 0:
                    self._exRouteIndex[fromStop+toStop] = routeChain

    ## recursion
    def _extend_route(self, fromStop, toStop, chainRoute):
        result = []
        if fromStop not in self.fromStops:
            return result
        for elRoute in chainRoute:
            if fromStop == elRoute.fromStop:
                return result

        if fromStop + toStop in self._routes:
            option = chainRoute.copy()
            option.append(self._routes[fromStop + toStop])
            result.append(option)

        ## fromStop in fromStops list    and    fromStop+toStop not in self._routes
        for childRoute in self.fromStops[fromStop]:
            option = chainRoute.copy()
            option.append(childRoute)
            nextStep = self._extend_route(childRoute.toStop, toStop, option)
            for aChain in nextStep:
                result.append(aChain)

        return result

    ## @route
    def exist(self, route):
        if route in self._routes:
            return True
        return False

    ## @route: format string
    def get_weight(self, route):
        if self.exist(route):
            return self._routes[route].weight
        return 0

    def get_extend_routes(self, fromStop, toStop):
        if fromStop + toStop not in self._exRouteIndex:
            return []
        else:
            return self._exRouteIndex[fromStop+toStop]


## A search class
class SearchRoute(object):

    ## @rtData: format dict
    def __init__(self, rtData):
        if type(rtData) != dict:
            raise "param wrong type"
        self.rtSet = RouteSet(rtData)

    ## @stopList
    ## return weight
    def search_weight(self, stopList):
        weight = 0
        idx = 0
        while idx < len(stopList) - 1:
            route = stopList[idx] + stopList[idx+1]
            if self.rtSet.exist(route):
                weight += self.rtSet.get_weight(route)
            else:
                return 'NO SUCH ROUTE'
            idx += 1
            
        return weight

    ## @fromStop
    ## @toStop
    ## return weight
    def search_shortest_weight(self, fromStop, toStop):
        shortestWeight = -1
        routeList = self.rtSet.get_extend_routes(fromStop, toStop)
        
        for route in routeList:
            weight = 0
            for nd in route:
                weight += nd.weight
            if shortestWeight < 0 or weight < shortestWeight:
                shortestWeight = weight

        return shortestWeight

    ## @max: weight should less than this number
    ## return [option1, option2, option2, ...]
    def search_options_max_weight(self, fromStop, toStop, maxWeight):
        optionList = []
        routeList = self.rtSet.get_extend_routes(fromStop, toStop)
        for route in routeList:
            weight = 0
            for nd in route:
                weight += nd.weight
            if weight < maxWeight:
                optionList.append(route)
                childOptionList = self.search_options_max_weight(toStop, toStop, maxWeight - weight)
                for childRoute in childOptionList:
                    optionList.append(route + childRoute)

        return optionList

    ## @fromStop
    ## @toStop
    ## return [option1, option2, option3, ...]
    def search_options_fix_stop(self, fromStop, toStop, fixStop):
        optionList = []
        routeList = self.rtSet.get_extend_routes(fromStop, toStop)
        for route in routeList:
            if len(route) > fixStop:
                continue
            elif len(route) == fixStop:
                if route in optionList:
                    continue
                optionList.append(route)
            else:
                ## must be '<'
                childList = self.search_options_fix_stop(toStop, toStop, fixStop - len(route))
                for childRoute in childList:
                    if route + childRoute in optionList:
                        continue
                    optionList.append(route + childRoute)

        return optionList

    ## @fromStop
    ## @toStop
    ## @maxStop
    def search_options_max_stop(self, fromStop, toStop, maxStop):
        optionList = []
        routeList = self.rtSet.get_extend_routes(fromStop, toStop)
        for route in routeList:
            if len(route) > maxStop:
                continue
            optionList.append(route)

        return optionList




if __name__ == '__main__':
    data = {
             "AB":5, 
             "BC":4, 
             "CD":8, 
             "DC":8, 
             "DE":6, 
             "AD":5, 
             "CE":2, 
             "EB":3, 
             "AE":7
           }
    sr = SearchRoute(data)
    ## 1. The distance of the route A-B-C.
    print("Output #1: " + str(sr.search_weight(['A', 'B', 'C'])))
    ## 2. The distance of the route A-D.
    print("Output #2: " + str(sr.search_weight(['A', 'D'])))
    ## 3. The distance of the route A-D-C.
    print("Output #3: " + str(sr.search_weight(['A', 'D', 'C'])))
    ## 4. The distance of the route A-E-B-C-D.
    print("Output #4: " + str(sr.search_weight(['A', 'E', 'B', 'C', 'D'])))
    ## 5. The distance of the route A-E-D.
    print("Output #5: " + str(sr.search_weight(['A', 'E', 'D'])))
    ## 6. The number of trips starting at C and ending at C with a maximum of 3 stops.  
    ##    In the sample data below, there are two such trips: C-D-C (2 stops). and C-E-B-C (3 stops).
    options = sr.search_options_max_stop('C', 'C', 3)
    print("Output #6: " + str(len(options)))
    ## 7. The number of trips starting at A and ending at C with exactly 4 stops.
    ##    In the sample data below, there are three such trips: A to C (via B,C,D); A
    ##    to C (via D,C,D); and A to C (via D,E,B).
    options = sr.search_options_fix_stop('A', 'C', 4)
    print("Output #7: " + str(len(options)))
    ''' ## details
    for op in options:
        rest = []
        for o in op:
            rest.append(o.route)
        print(','.join(rest))
    '''
    ## 8. The length of the shortest route (in terms of distance to travel) from A to C.
    print("Output #8: " + str(sr.search_shortest_weight('A', 'C')))
    ## 9. The length of the shortest route (in terms of distance to travel) from B to B.
    print("Output #9: " + str(sr.search_shortest_weight('B', 'B')))
    ## 10.The number of different routes from C to C with a distance of less than 30.
    ## In the sample data, the trips are: CDC, CEBC, CEBCDC, CDCEBC, CDEBC, CEBCEBC, CEBCEBCEBC.
    options = sr.search_options_max_weight('C', 'C', 30)
    print("Output #10: " + str(len(options)))
