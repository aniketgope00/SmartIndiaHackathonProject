#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Eclipse SUMO, Simulation of Urban MObility; see https://eclipse.dev/sumo
# Copyright (C) 2021-2024 German Aerospace Center (DLR) and others.
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License 2.0 which is available at
# https://www.eclipse.org/legal/epl-2.0/
# This Source Code may also be made available under the following Secondary
# Licenses when the conditions for such availability set forth in the Eclipse
# Public License 2.0 are satisfied: GNU General Public License, version 2
# or later which is available at
# https://www.gnu.org/licenses/old-licenses/gpl-2.0-standalone.html
# SPDX-License-Identifier: EPL-2.0 OR GPL-2.0-or-later

# @file    drtOrtools.py
# @author  Philip Ritzer
# @author  Johannes Rummel
# @author  Mirko Barthauer
# @date    2021-12-16

"""
Prototype online DRT algorithm using ortools via TraCI.
"""
from __future__ import print_function
from enum import Enum

import os
import pathlib
import sys

import numpy as np
import ortools_pdp

# we need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    sys.path.append(os.path.join(os.environ['SUMO_HOME'], 'tools'))

# SUMO modules
import sumolib  # noqa
import traci  # noqa

SPEED_DEFAULT = 20  # default vehicle speed in m/s
PENALTY_FACTOR = 5  # factor on penalty for rejecting requests


class CostType(Enum):
    DISTANCE = 1
    TIME = 2


def dispatch(reservations, fleet, time_limit, cost_type, drf, waiting_time, end,
             fix_allocation, solution_requests, penalty, verbose):
    """Dispatch using ortools."""
    if verbose:
        print('Start creating the model.')
    data = create_data_model(reservations, fleet, cost_type, drf, waiting_time, end,
                             fix_allocation, solution_requests, penalty, verbose)
    if verbose:
        print('Start solving the problem.')
    solution_ortools = ortools_pdp.main(data, time_limit, verbose)
    if verbose:
        print('Start interpreting the solution for SUMO.')
    solution_requests = solution_by_requests(solution_ortools, reservations, data, verbose)
    return solution_requests


def create_data_model(reservations, fleet, cost_type, drf, waiting_time, end,
                      fix_allocation, solution_requests, penalty, verbose):
    """Creates the data for the problem."""
    n_vehicles = len(fleet)
    # use only reservations that haven't been picked up yet; reservation.state!=8 (not picked up)
    dp_reservations = [res for res in reservations if res.state != 8]
    n_dp_reservations = len(dp_reservations)
    if verbose:
        print('dp reservations: %s' % ([res.id for res in dp_reservations]))
    # use only reservations that already haven been picked up; reservation.state==8 (picked up)
    do_reservations = [res for res in reservations if res.state == 8]
    n_do_reservations = len(do_reservations)
    if verbose:
        print('do reservations: %s' % ([res.id for res in do_reservations]))

    # edges: [depot_id, res_from_id, ..., res_to_id, ..., res_dropoff_id, ..., veh_start_id, ...]
    edges = ['depot']
    for reservation in dp_reservations:
        from_edge = reservation.fromEdge
        edges.append(from_edge)
        # add new attribute 'from_node' to the reservation
        setattr(reservation, 'from_node', len(edges) - 1)
        if verbose:
            print('Reservation %s starts at edge %s' % (reservation.id, from_edge))
    for reservation in dp_reservations:
        to_edge = reservation.toEdge
        edges.append(to_edge)
        # add new attribute 'to_node' to the reservation
        setattr(reservation, 'to_node', len(edges) - 1)
        if verbose:
            print('Reservation %s ends at edge %s' % (reservation.id, to_edge))
    for reservation in dp_reservations:
        if reservation.state == 1 or reservation.state == 2:
            setattr(reservation, 'is_new', True)
        else:
            setattr(reservation, 'is_new', False)
    for reservation in do_reservations:
        to_edge = reservation.toEdge
        edges.append(to_edge)
        # add new attribute 'to_node' to the reservation
        setattr(reservation, 'to_node', len(edges) - 1)
        if verbose:
            print('Drop-off of reservation %s at edge %s' % (reservation.id, to_edge))

    starts = []
    types_vehicle = []
    vehicle_capacities = []
    for id_vehicle in fleet:
        edge_vehicle = traci.vehicle.getRoadID(id_vehicle)
        starts.append(edge_vehicle)
        edges.append(edge_vehicle)
        vehicle_capacities.append(traci.vehicle.getPersonCapacity(id_vehicle))
        types_vehicle.append(traci.vehicle.getTypeID(id_vehicle))
    types_vehicles_unique = list(set(types_vehicle))
    if len(types_vehicles_unique) > 1:
        raise Exception("Only one vehicle type is supported.")
        # TODO support more than one vehicle type
    else:
        type_vehicle = types_vehicles_unique[0]
    pickup_indices = range(1, 1 + n_dp_reservations)
    dropoff_indices = range(1 + n_dp_reservations, 1 + 2*n_dp_reservations + n_do_reservations)
    cost_matrix, time_matrix = get_cost_matrix(edges, type_vehicle, cost_type, pickup_indices, dropoff_indices)

    # safe cost and time matrix
    # if verbose:
    #    import csv
    #    with open("cost_matrix.csv", 'a') as cost_file:
    #        wr = csv.writer(cost_file)
    #        wr.writerows(cost_matrix)
    #    with open("time_matrix.csv", 'a') as time_file:
    #        wr = csv.writer(time_file)
    #        wr.writerows(time_matrix)

    # add "direct route cost" to the requests:
    for res in reservations:
        if hasattr(res, 'direct_route_cost'):
            continue
        if hasattr(res, 'from_node'):
            setattr(res, 'direct_route_cost', cost_matrix[res.from_node][res.to_node])
            if verbose:
                print('Reservation %s has direct route costs %s' % (res.id, res.direct_route_cost))
        else:
            # TODO: use 'historical data' from dict in get_cost_matrix instead
            route = traci.simulation.findRoute(res.fromEdge, res.toEdge, vType=type_vehicle)
            if cost_type == CostType.TIME:
                direct_route_cost = route.travelTime
            elif cost_type == CostType.DISTANCE:
                direct_route_cost = route.length
            else:
                raise ValueError("Cannot set given cost ('%s')." % (cost_type))
            setattr(res, 'direct_route_cost', direct_route_cost)

    # add "current route cost" to the already picked up reservations:
    for res in do_reservations:
        person_id = res.persons[0]
        stage = traci.person.getStage(person_id, 0)
        # stage type 3 is defined as 'driving'
        assert stage.type == 3
        # if verbose:
        #    print("travel time: ", stage.travelTime)
        #    print("travel length: ", stage.length)
        #    print("travel cost: ", stage.cost)
        if cost_type == CostType.DISTANCE:
            setattr(res, 'current_route_cost', stage.length)
        elif cost_type == CostType.TIME:
            setattr(res, 'current_route_cost', stage.travelTime)
        else:
            raise ValueError("Cannot set given cost ('%s')." % (cost_type))

    # pd_nodes = list([from_node, to_node, is_new])
    # start from_node with 1 (0 is for depot)
    # pd_nodes = [[ii+1, n_dp_reservations+ii+1, (dp_reservations[ii].state == 1 | dp_reservations[ii].state == 2)]
    #             for ii in range(0, n_dp_reservations)]
    # do_node = list(dropoff_node)
    # do_nodes = [ii + 1 + 2*n_dp_reservations for ii in range(0, n_do_reservations)]
    ii = 1 + 2*n_dp_reservations + n_do_reservations
    # node to start from
    start_nodes = [jj for jj in range(ii, ii + n_vehicles)]

    # increase demand (load) of the vehicle for each outstanding drop off
    veh_demand = [0] * n_vehicles
    for v_i, id_vehicle in enumerate(fleet):
        for reservation in do_reservations:
            entered_persons = traci.vehicle.getPersonIDList(id_vehicle)
            if reservation.persons[0] in entered_persons:
                veh_demand[v_i] += 1
                setattr(reservation, 'vehicle', id_vehicle)  # id of assigned vehicle (from SUMO input)
                setattr(reservation, 'vehicle_index', v_i)  # index of assigned vehicle [0, ..., n_v -1]

    # get time windows
    time_windows = get_time_windows(reservations, fleet, end)

    data = {}
    data['depot'] = 0  # node_id of the depot
    data['cost_matrix'] = cost_matrix
    data['time_matrix'] = time_matrix
    data['pickups_deliveries'] = dp_reservations
    data['dropoffs'] = do_reservations
    data['num_vehicles'] = n_vehicles
    data['starts'] = start_nodes
    data['ends'] = n_vehicles * [0]  # end at 'depot', which is is anywere
    data['demands'] = [0] + n_dp_reservations*[1] + n_dp_reservations*[-1] + n_do_reservations*[-1] + veh_demand
    data['vehicle_capacities'] = vehicle_capacities
    data['drf'] = drf
    data['waiting_time'] = waiting_time
    data['time_windows'] = time_windows
    data['fix_allocation'] = fix_allocation
    data['max_time'] = end
    data['initial_routes'] = solution_requests
    data['penalty'] = int(penalty)
    return data


def get_network_path(sumo_config):
    """Get path to SUMO network from config file."""
    sumo_config = pathlib.Path(sumo_config)
    net_file = list(sumolib.xml.parse(sumo_config, "net-file"))
    net_filename = net_file[0].getAttribute("value")
    net_path = pathlib.Path(net_filename)
    if net_path.is_absolute():
        return net_path
    else:
        return sumo_config.parent / net_path


def get_network_dimension(sumo_config, cost_type):
    """Get the rough network dimension."""
    net_path = get_network_path(sumo_config)
    net = sumolib.net.readNet(net_path)
    # diameter of bounding box
    diameter = net.getBBoxDiameter()
    if cost_type.name == "DISTANCE":
        dimension = diameter
    if cost_type.name == "TIME":
        # convert distance to time assuming default speed
        dimension = diameter / SPEED_DEFAULT
    return dimension


def get_penalty(sumo_config, cost_type, penalty_factor=PENALTY_FACTOR):
    """Define penalty for rejecting requests."""
    dimension = get_network_dimension(sumo_config, cost_type)
    penalty = dimension * penalty_factor
    return int(penalty)


def get_time_windows(reservations, fleet, end):
    """returns a list of pairs with earliest and latest time"""
    # order must be the same as for the cost_matrix and demands
    # edges: [depot_id, res_from_id, ..., res_to_id, ..., res_dropoff_id, ..., veh_start_id, ...]
    time_windows = []
    # start at depot should be the current simulation time:
    current_time = round(traci.simulation.getTime())
    max_time = round(end)
    time_windows.append((current_time, max_time))
    # use reservations that haven't been picked up yet; reservation.state!=8 (not picked up)
    dp_reservations = [res for res in reservations if res.state != 8]
    for res in dp_reservations:
        person_id = res.persons[0]
        pickup_earliest = traci.person.getParameter(person_id, "pickup_earliest")
        if pickup_earliest:
            pickup_earliest = round(float(pickup_earliest))
        else:
            pickup_earliest = current_time
        time_windows.append((pickup_earliest, max_time))
    for res in dp_reservations:
        person_id = res.persons[0]
        dropoff_latest = traci.person.getParameter(person_id, "dropoff_latest")
        if dropoff_latest:
            dropoff_latest = round(float(dropoff_latest))
        else:
            dropoff_latest = max_time
        time_windows.append((current_time, dropoff_latest))
    # use reservations that already haven been picked up; reservation.state==8 (picked up)
    do_reservations = [res for res in reservations if res.state == 8]
    for res in do_reservations:
        person_id = res.persons[0]
        dropoff_latest = traci.person.getParameter(person_id, "dropoff_latest")
        if dropoff_latest:
            dropoff_latest = round(float(dropoff_latest))
        else:
            dropoff_latest = max_time
        time_windows.append((current_time, dropoff_latest))
    # start point of the vehicles (TODO: is that needed?)
    for _ in fleet:
        time_windows.append((current_time, max_time))
    return time_windows


def get_max_time():
    max_sim_time = traci.simulation.getEndTime()
    if max_sim_time == -1:
        return 90000
    else:
        return max_sim_time


# TODO: If cost_type is TIME, remove cost_matrix and cost_dict.
def get_cost_matrix(edges, type_vehicle, cost_type, pickup_indices, dropoff_indices):
    """Get cost matrix between edges.
    Index in cost matrix is the same as the node index of the constraint solver."""

    id_vehicle = traci.vehicle.getTaxiFleet(-1)[0]  # take a vehicle
    id_vtype = traci.vehicle.getTypeID(id_vehicle)  # take its vtype
    boardingDuration_param = traci.vehicletype.getBoardingDuration(id_vtype)
    boardingDuration = 0 if boardingDuration_param == '' else round(float(boardingDuration_param))
    pickUpDuration_param = traci.vehicle.getParameter(id_vehicle, 'device.taxi.pickUpDuration')
    pickUpDuration = 0 if pickUpDuration_param == '' else round(float(pickUpDuration_param))
    dropOffDuration_param = traci.vehicle.getParameter(id_vehicle, 'device.taxi.dropOffDuration')
    dropOffDuration = 0 if dropOffDuration_param == '' else round(float(dropOffDuration_param))
    n_edges = len(edges)
    time_matrix = np.zeros([n_edges, n_edges], dtype=int)
    cost_matrix = np.zeros([n_edges, n_edges], dtype=int)
    time_dict = {}
    cost_dict = {}
    # TODO initialize cost_dict and time_dict{} in run() and update for speed improvement
    for ii, edge_from in enumerate(edges):
        for jj, edge_to in enumerate(edges):
            if (edge_from, edge_to) in cost_dict:
                # get costs from previous call
                time_matrix[ii][jj] = time_dict[(edge_from, edge_to)]
                cost_matrix[ii][jj] = cost_dict[(edge_from, edge_to)]
                continue
            # cost to depot should be always 0
            # (means there is no way to depot in the end)
            if edge_from == 'depot' or edge_to == 'depot':
                time_matrix[ii][jj] = 0
                cost_matrix[ii][jj] = 0
                continue
            if ii == jj:
                time_matrix[ii][jj] = 0
                cost_matrix[ii][jj] = 0
                continue
            route = traci.simulation.findRoute(edge_from, edge_to, vType=type_vehicle)
            time_matrix[ii][jj] = round(route.travelTime)
            if ii in pickup_indices:
                time_matrix[ii][jj] += pickUpDuration  # add pickup_duration
                time_matrix[ii][jj] += boardingDuration  # add boarding_duration
            if jj in dropoff_indices:
                time_matrix[ii][jj] += dropOffDuration  # add dropoff_duration
            time_dict[(edge_from, edge_to)] = time_matrix[ii][jj]
            if cost_type == CostType.TIME:
                cost_matrix[ii][jj] = time_matrix[ii][jj]
                cost_dict[(edge_from, edge_to)] = time_dict[(edge_from, edge_to)]
            elif cost_type == CostType.DISTANCE:
                cost_matrix[ii][jj] = round(route.length)
                cost_dict[(edge_from, edge_to)] = round(route.length)
    return cost_matrix.tolist(), time_matrix.tolist()


def solution_by_requests(solution_ortools, reservations, data, verbose=False):
    """Translate solution from ortools to SUMO requests."""
    if solution_ortools is None:
        return None

    # dp_reservations = [res for res in reservations if res.state != 8]

    route2request = {}
    for res in data["pickups_deliveries"]:
        route2request[res.from_node] = res.id
        route2request[res.to_node] = res.id
    for res in data['dropoffs']:  # for each vehicle
        route2request[res.to_node] = res.id

    solution_requests = {}
    for key in solution_ortools:  # key is the vehicle number (0,1,...)
        solution = [[], [], []]  # request order, costs, node order
        for i_route in solution_ortools[key][0][1:-1]:  # take only the routes ([0]) without the start node ([1:-1])
            if i_route in route2request:
                solution[0].append(route2request[i_route])  # add request id to route
                res = [res for res in reservations if res.id == route2request[i_route]][0]  # get the reservation
                setattr(res, 'vehicle_index', key)
            else:
                if verbose:
                    print('!solution ignored: %s' % (i_route))
                continue
            solution[1] = solution_ortools[key][1]  # costs
            solution[2].append(i_route)  # node
        solution_requests[key] = solution
    return solution_requests


def run(penalty, end=None, interval=30, time_limit=10, cost_type='distance', drf=1.5, waiting_time=900,
        fix_allocation=False, verbose=False):
    """
    Execute the TraCI control loop and run the scenario.

    Parameters
    ----------
    penalty: int
        Penalty for rejecting requests.
    end : int, optional
        Final time step of simulation. The default is 90000.
        This option can be ignored by giving a negative value.
    interval : int, optional
        Dispatching interval in s. The default is 30.
    time_limit: float, optional
        Time limit for solver in s. The default is 10.
    cost_type: str, optional
        Type of costs. The default is 'distance'. Another option is 'time'.
    verbose : bool, optional
        Controls whether debug information is printed. The default is True.
    """
    running = True
    timestep = traci.simulation.getTime()
    if not end:
        end = get_max_time()

    if verbose:
        print('Simulation parameters:')
        print(f'  end: {end}')
        print(f'  interval: {interval}')
        print(f'  time_limit: {time_limit}')
        print(f'  cost_type: {cost_type}')
        print(f'  drf: {drf}')
        print(f'  waiting_time: {waiting_time}')
        print(f'  fix_allocation: {fix_allocation}')

    reservations_all = list()
    solution_requests = None
    while running:

        traci.simulationStep(timestep)

        # termination condition
        if timestep > end:
            running = False
            continue

        if not traci.vehicle.getTaxiFleet(-1) and timestep < end:
            timestep += interval
            continue

        reservations_new = traci.person.getTaxiReservations(1)
        if verbose:
            print("timestep: ", timestep)
            res_waiting = [res.id for res in traci.person.getTaxiReservations(2)]
            res_pickup = [res.id for res in traci.person.getTaxiReservations(4)]
            res_transport = [res.id for res in traci.person.getTaxiReservations(8)]
            if res_waiting:
                print("Reservations waiting:", res_waiting)
            if res_pickup:
                print("Reservations being picked up:", res_pickup)
            if res_transport:
                print("Reservations en route:", res_transport)
            fleet_empty = traci.vehicle.getTaxiFleet(0)
            fleet_pickup = traci.vehicle.getTaxiFleet(1)
            fleet_occupied = traci.vehicle.getTaxiFleet(2)
            fleet_occupied_pickup = traci.vehicle.getTaxiFleet(3)
            if fleet_empty:
                print("Taxis empty:", fleet_empty)
            if fleet_pickup:
                print("Taxis picking up:", fleet_pickup)
            if fleet_occupied:
                print("Taxis occupied:", fleet_occupied)
            if fleet_occupied_pickup:
                print("Taxis occupied and picking up:", fleet_occupied_pickup)

        fleet = traci.vehicle.getTaxiFleet(-1)
        reservations_not_assigned = traci.person.getTaxiReservations(3)

        # find and remove unassigned reservations that cannot be picked up by time
        reservations_removed = [
            res for res in reservations_not_assigned if res.reservationTime + waiting_time < timestep]
        for res in reservations_removed:
            for person in res.persons:
                traci.person.removeStages(person)
        reservations_new = [res for res in reservations_new if res not in reservations_removed]
        if verbose:
            if reservations_removed:
                print(f"Reservations rejected: {[res.id for res in reservations_removed]}")

        # if fix_allocation=True only take new reservations from traci
        # and add to all_reservations to keep the vehicle allocation for the older reservations
        current_reservations = traci.person.getTaxiReservations(0)
        if fix_allocation:
            reservations_all += reservations_new
            current_res_ids = [res.id for res in current_reservations]
            # remove completed reservations
            reservations_all = [res for res in reservations_all if res.id in current_res_ids]
            for res in reservations_all:  # update reservation state
                if res.id in current_res_ids:
                    res.state = [cur_res for cur_res in current_reservations if cur_res.id == res.id][0].state
        else:
            reservations_all = current_reservations

        # if reservations_all:  # used for debugging
        if reservations_not_assigned:
            if verbose:
                print("Solve CPDP")
            solution_requests = dispatch(reservations_all, fleet, time_limit, cost_type, drf, waiting_time, int(end),
                                         fix_allocation, solution_requests, penalty, verbose)
            if solution_requests is not None:
                for index_vehicle, vehicle_requests in solution_requests.items():  # for each vehicle
                    id_vehicle = fleet[index_vehicle]
                    reservations_order = [res_id for res_id in vehicle_requests[0]]  # [0] for route
                    if verbose:
                        print("Dispatching %s with %s" % (id_vehicle, reservations_order))
                        print("Costs for %s: %s" % (id_vehicle, vehicle_requests[1]))
                    if fix_allocation and not reservations_order:  # ignore empty reservations if allocation is fixed
                        continue
                    traci.vehicle.dispatchTaxi(id_vehicle, reservations_order)  # overwrite existing dispatch
            else:
                if verbose:
                    print("Found no solution, continue...")

        timestep += interval

    # Finish
    traci.close()
    sys.stdout.flush()


def get_arguments():
    """Get command line arguments."""
    ap = sumolib.options.ArgumentParser()
    ap.add_argument("-s", "--sumo-config", required=True, category="input", type=ap.file,
                    help="sumo config file to run")
    ap.add_argument("-e", "--end", type=ap.time,
                    help="time step to end simulation at")
    ap.add_argument("-i", "--interval", type=ap.time, default=30,
                    help="dispatching interval in s")
    ap.add_argument("-n", "--nogui", action="store_true", default=False,
                    help="run the commandline version of sumo")
    ap.add_argument("-v", "--verbose", action="store_true", default=False,
                    help="print debug information")
    ap.add_argument("-t", "--time-limit", type=ap.time, default=10,
                    help="time limit for solver in s")
    ap.add_argument("-d", "--cost-type", default="distance",
                    help="type of costs to minimize (distance or time)")
    ap.add_argument("-f", "--drf", type=float, default=1.5,
                    help="direct route factor to calculate maximum cost "
                         "for a single dropoff-pickup route (set to -1, if you do not need it)")
    ap.add_argument("-a", "--fix-allocation", action="store_true", default=False,
                    help="if true: after first solution the allocation of reservations to vehicles" +
                    "does not change anymore")
    ap.add_argument("-w", "--waiting-time", type=ap.time, default=900,
                    help="maximum waiting time to serve a request in s")
    ap.add_argument("-p", "--penalty-factor", type=float, default=PENALTY_FACTOR,
                    help="factor on penalty for rejecting requests")
    ap.add_argument("--trace-file", type=ap.file,
                    help="log file for TraCI debugging")
    return ap.parse_args()


def check_set_arguments(arguments):
    if arguments.nogui:
        arguments.sumoBinary = sumolib.checkBinary('sumo')
    else:
        arguments.sumoBinary = sumolib.checkBinary('sumo-gui')

    # set cost type
    if arguments.cost_type == "distance":
        arguments.cost_type = CostType.DISTANCE
    elif arguments.cost_type == "time":
        arguments.cost_type = CostType.TIME
    else:
        raise ValueError(f"Wrong cost type '{arguments.cost_type}'. Only 'distance' and 'time' are allowed.")

    if arguments.drf < 1 and arguments.drf != -1:
        raise ValueError(
            f"Wrong value for drf '{arguments.drf}'. Value must be equal or greater than 1. -1 means no drf is used.")

    if arguments.waiting_time < 0:
        raise ValueError(
            f"Wrong value for waiting time '{arguments.waiting_time}'. Value must be equal or greater than 0.")


if __name__ == "__main__":

    arguments = get_arguments()
    check_set_arguments(arguments)
    # this script has been called from the command line. It will start sumo as a
    # server, then connect and run

    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
    traci.start([arguments.sumoBinary, "-c", arguments.sumo_config], traceFile=arguments.trace_file)

    # get penalty
    penalty = get_penalty(arguments.sumo_config, arguments.cost_type, arguments.penalty_factor)

    run(penalty, arguments.end, arguments.interval, arguments.time_limit, arguments.cost_type, arguments.drf,
        arguments.waiting_time, arguments.fix_allocation, arguments.verbose)
