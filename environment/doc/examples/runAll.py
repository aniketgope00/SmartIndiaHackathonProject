#!/usr/bin/env python
import subprocess, sys, os, multiprocessing
from os.path import abspath, dirname, join
THIS_DIR = abspath(dirname(__file__))
SUMO_HOME = os.environ.get("SUMO_HOME", dirname(dirname(THIS_DIR)))
os.environ["SUMO_HOME"] = SUMO_HOME
calls = [
    (r"dfrouter", [join(SUMO_HOME, "bin", "dfrouter"), "--write-license", "--include-unused-routes", "--measure-files", "input_tri_flows.txt", "--keep-longer-routes", "--net-file=input_tri.net.xml", "--detector-files=input_tri.det.xml", "--routes-output", "routes.rou.xml", "--emitters-output", "emitters.add.xml", "-e", "60"], r"dfrouter"),
    (r"duarouter\flows2routes", [join(SUMO_HOME, "bin", "duarouter"), "--no-step-log", "--write-license", "--net-file=input_net.net.xml", "--route-files=input_flows.flows.xml", "-o", "routes.rou.xml"], r"duarouter\flows2routes"),
    (r"duarouter\flows2routes_100s_interval", [join(SUMO_HOME, "bin", "duarouter"), "--no-step-log", "--write-license", "--net-file=input_net.net.xml", "--route-files=input_flows.flows.xml", "-o", "routes.rou.xml"], r"duarouter\flows2routes_100s_interval"),
    (r"duarouter\flows2routes_100s_interval_ext", [join(SUMO_HOME, "bin", "duarouter"), "--no-step-log", "--write-license", "--net-file=input_net.net.xml", "--route-files=input_flows.flows.xml", "-o", "routes.rou.xml"], r"duarouter\flows2routes_100s_interval_ext"),
    (r"duarouter\flows2routes_200s_interval", [join(SUMO_HOME, "bin", "duarouter"), "--no-step-log", "--write-license", "--net-file=input_net.net.xml", "--route-files=input_flows.flows.xml", "-o", "routes.rou.xml"], r"duarouter\flows2routes_200s_interval"),
    (r"duarouter\trips2routes", [join(SUMO_HOME, "bin", "duarouter"), "--no-step-log", "--write-license", "--net-file=input_net.net.xml", "--route-files=input_trips.trips.xml", "-o", "routes.rou.xml"], r"duarouter\trips2routes"),
    (r"jtrrouter\turns", [join(SUMO_HOME, "bin", "jtrrouter"), "--no-step-log", "--write-license", "--output-file=routes.rou.xml", "--net-file=input_net.net.xml", "--route-files=input_flows.flows.xml", "--sinks=end", "--turns=input_turns.turns.xml", "--ignore-errors"], r"jtrrouter\turns"),
    (r"jtrrouter\straight_only_sinks", [join(SUMO_HOME, "bin", "jtrrouter"), "--no-step-log", "--write-license", "--net-file=input_net.net.xml", "--route-files=input_flows.flows.xml", "--output-file=routes.rou.xml", "--turn-defaults=0,100,0,0", "--sinks=end", "--ignore-errors"], r"jtrrouter\straight_only_sinks"),
    (r"netconvert\connections\cross3l_edge2edge_conns", [join(SUMO_HOME, "bin", "netconvert"), "--write-license", "--edge-files=input_edges.edg.xml", "--connection-files", "input_connections.con.xml", "--node-files=input_nodes.nod.xml", "--output=net.net.xml", "--speed-in-kmh"], r"netconvert\connections\cross3l_edge2edge_conns"),
    (r"netconvert\connections\cross3l_lane2lane_conns", [join(SUMO_HOME, "bin", "netconvert"), "--write-license", "--edge-files=input_edges.edg.xml", "--connection-files=input_connections.con.xml", "--node-files=input_nodes.nod.xml", "--output=net.net.xml", "--speed-in-kmh"], r"netconvert\connections\cross3l_lane2lane_conns"),
    (r"netconvert\connections\cross3l_no_turnarounds", [join(SUMO_HOME, "bin", "netconvert"), "--write-license", "--edge-files=input_edges.edg.xml", "--node-files=input_nodes.nod.xml", "--output=net.net.xml", "--speed-in-kmh", "--no-turnarounds"], r"netconvert\connections\cross3l_no_turnarounds"),
    (r"netconvert\connections\cross3l_prohibitions", [join(SUMO_HOME, "bin", "netconvert"), "--write-license", "--edge-files=input_edges.edg.xml", "--connection-files", "input_connections.con.xml", "--node-files=input_nodes.nod.xml", "--output=net.net.xml", "--speed-in-kmh"], r"netconvert\connections\cross3l_prohibitions"),
    (r"netconvert\connections\cross3l_unconstrained", [join(SUMO_HOME, "bin", "netconvert"), "--write-license", "--edge-files=input_edges.edg.xml", "--node-files=input_nodes.nod.xml", "--output=net.net.xml", "--speed-in-kmh"], r"netconvert\connections\cross3l_unconstrained"),
    (r"netconvert\hokkaido", [join(SUMO_HOME, "bin", "netconvert"), "--write-license", "--edge-files=input_edges.edg.xml", "--node-files=input_nodes.nod.xml", "--output=net.net.xml", "--plain-output=plain", "--plain.extend-edge-shape"], r"netconvert\hokkaido"),
    (r"netconvert\dlr-testtrack", [join(SUMO_HOME, "bin", "netconvert"), "--write-license", "--edge-files=input_edges.edg.xml", "--node-files=input_nodes.nod.xml", "--connection-files=input_connections.con.xml", "--output=net.net.xml", "--no-turnarounds"], r"netconvert\dlr-testtrack"),
    (r"netconvert\speed_in_kmh\cross_notypes_kmh", [join(SUMO_HOME, "bin", "netconvert"), "--write-license", "--edge-files=input_edges.edg.xml", "--node-files=input_nodes.nod.xml", "--output=net.net.xml", "--speed-in-kmh"], r"netconvert\speed_in_kmh\cross_notypes_kmh"),
    (r"netconvert\speed_in_kmh\cross_usingtypes_kmh", [join(SUMO_HOME, "bin", "netconvert"), "--write-license", "--edge-files=input_edges.edg.xml", "--node-files=input_nodes.nod.xml", "--type-files=input_types.typ.xml", "--output=net.net.xml", "--speed-in-kmh"], r"netconvert\speed_in_kmh\cross_usingtypes_kmh"),
    (r"netconvert\types\cross_notypes", [join(SUMO_HOME, "bin", "netconvert"), "--write-license", "--edge-files=input_edges.edg.xml", "--node-files=input_nodes.nod.xml", "--output=net.net.xml"], r"netconvert\types\cross_notypes"),
    (r"netconvert\types\cross_usingtypes", [join(SUMO_HOME, "bin", "netconvert"), "--write-license", "--edge-files=input_edges.edg.xml", "--node-files=input_nodes.nod.xml", "--type-files=input_types.typ.xml", "--output=net.net.xml"], r"netconvert\types\cross_usingtypes"),
    (r"netconvert\OSM\adlershof_dlr", [join(SUMO_HOME, "bin", "netconvert"), "--write-license", "--no-internal-links", "--osm-files", "osm.xml", "-v", "--proj.utm", "--output.street-names", "--plain-output-prefix", "plain", "--proj.plain-geo", "--output", "net.net.xml", "--tls.red.time", "10"], r"netconvert\OSM\adlershof_dlr"),
    (r"sumo\hokkaido", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--no-step-log", "--no-duration-log", "--net-file=net.net.xml", "--routes=input_routes.rou.xml", "-b", "0", "-e", "10000"], r"sumo\hokkaido"),
    (r"sumo\variable_speed_signs", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "-b", "0", "-e", "1000", "--no-step-log", "--no-duration-log", "--net-file=net.net.xml", "--routes=input_routes.rou.xml", "-a", "input_additional.add.xml,input_additional2.add.xml"], r"sumo\variable_speed_signs"),
    (r"sumo\variable_speed_signs", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--mesosim", "-b", "0", "-e", "1000", "--no-step-log", "--no-duration-log", "--net-file=net.net.xml", "--routes=input_routes.rou.xml", "-a", "input_additional.add.xml,input_additional2.add.xml"], r"sumo\variable_speed_signs"),
    (r"sumo\vehicle_stops", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--no-step-log", "--no-duration-log", "--net-file=net.net.xml", "--routes=input_routes.rou.xml", "--vehroute-output", "vehroutes.xml", "--stop-output", "stopinfos.xml"], r"sumo\vehicle_stops"),
    (r"sumo\vehicle_stops", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--step-method.ballistic", "--no-step-log", "--no-duration-log", "--net-file=net.net.xml", "--routes=input_routes.rou.xml", "--vehroute-output", "vehroutes.xml", "--stop-output", "stopinfos.xml"], r"sumo\vehicle_stops"),
    (r"sumo\vehicle_stops", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--mesosim", "--no-step-log", "--no-duration-log", "--net-file=net.net.xml", "--routes=input_routes.rou.xml", "--vehroute-output", "vehroutes.xml", "--stop-output", "stopinfos.xml"], r"sumo\vehicle_stops"),
    (r"sumo\busses", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--no-step-log", "--no-duration-log", "--net-file=net.net.xml", "-a=input_additional.add.xml", "--vehroutes=vehroutes.xml"], r"sumo\busses"),
    (r"sumo\busses", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--step-method.ballistic", "--no-step-log", "--no-duration-log", "--net-file=net.net.xml", "-a=input_additional.add.xml", "--vehroutes=vehroutes.xml"], r"sumo\busses"),
    (r"sumo\angled_roadside_parking", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--no-step-log", "--no-duration-log", "-n", "net.net.xml", "--route-files=input_routes.rou.xml", "--additional-files=input_additional.add.xml", "--fcd-output", "fcd.xml", "--fcd-output.signals"], r"sumo\angled_roadside_parking"),
    (r"sumo\visualization\parade", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--no-step-log", "--no-duration-log", "--net-file=net.net.xml", "--routes=input_routes.rou.xml", "--time-to-teleport", "-1"], r"sumo\visualization\parade"),
    (r"sumo\visualization\paradePersons", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--no-step-log", "--no-duration-log", "--net-file=net.net.xml", "--routes=input_routes.rou.xml", "--time-to-teleport", "-1", "-a", "input_additional.add.xml", "-g", "settings.xml"], r"sumo\visualization\paradePersons"),
    (r"sumo\visualization\paradeContainers", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--no-step-log", "--no-duration-log", "--net-file=net.net.xml", "--routes=input_routes.rou.xml", "--time-to-teleport", "-1", "-g", "settings.xml", "-a", "input_additional.add.xml"], r"sumo\visualization\paradeContainers"),
    (r"sumo\output\cross3ltl_emission", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--no-step-log", "--no-duration-log", "--emission-output=emissions.xml", "--net-file=net.net.xml", "-r", "input_routes.rou.xml", "-b", "0", "-e", "120"], r"sumo\output\cross3ltl_emission"),
    (r"sumo\output\cross3ltl_emission", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--mesosim", "--no-step-log", "--no-duration-log", "--emission-output=emissions.xml", "--net-file=net.net.xml", "-r", "input_routes.rou.xml", "-b", "0", "-e", "120"], r"sumo\output\cross3ltl_emission"),
    (r"sumo\output\cross3ltl_emission", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--lateral-resolution", "0.8", "--no-step-log", "--no-duration-log", "--emission-output=emissions.xml", "--net-file=net.net.xml", "-r", "input_routes.rou.xml", "-b", "0", "-e", "120"], r"sumo\output\cross3ltl_emission"),
    (r"sumo\output\cross3ltl_fcd", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--no-step-log", "--no-duration-log", "--fcd-output=fcd.xml", "--net-file=net.net.xml", "-r", "input_routes.rou.xml", "-b", "0", "-e", "120"], r"sumo\output\cross3ltl_fcd"),
    (r"sumo\output\cross3ltl_fcd", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--mesosim", "--no-step-log", "--no-duration-log", "--fcd-output=fcd.xml", "--net-file=net.net.xml", "-r", "input_routes.rou.xml", "-b", "0", "-e", "120"], r"sumo\output\cross3ltl_fcd"),
    (r"sumo\output\cross3ltl_fcd", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--lateral-resolution", "0.8", "--no-step-log", "--no-duration-log", "--fcd-output=fcd.xml", "--net-file=net.net.xml", "-r", "input_routes.rou.xml", "-b", "0", "-e", "120"], r"sumo\output\cross3ltl_fcd"),
    (r"sumo\output\cross3ltl_full", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--no-step-log", "--no-duration-log", "--full-output=full.xml", "--net-file=net.net.xml", "-r", "input_routes.rou.xml", "-b", "0", "-e", "120"], r"sumo\output\cross3ltl_full"),
    (r"sumo\output\cross3ltl_full", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--mesosim", "--no-step-log", "--no-duration-log", "--full-output=full.xml", "--net-file=net.net.xml", "-r", "input_routes.rou.xml", "-b", "0", "-e", "120"], r"sumo\output\cross3ltl_full"),
    (r"sumo\output\cross3ltl_full", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--lateral-resolution", "0.8", "--no-step-log", "--no-duration-log", "--full-output=full.xml", "--net-file=net.net.xml", "-r", "input_routes.rou.xml", "-b", "0", "-e", "120"], r"sumo\output\cross3ltl_full"),
    (r"sumo\output\cross3ltl_inductloops", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--no-step-log", "--no-duration-log", "--net-file=net.net.xml", "-r", "input_routes.rou.xml", "-a", "input_additional.add.xml", "-b", "0", "-e", "1000"], r"sumo\output\cross3ltl_inductloops"),
    (r"sumo\output\cross3ltl_inductloops", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--mesosim", "--no-step-log", "--no-duration-log", "--net-file=net.net.xml", "-r", "input_routes.rou.xml", "-a", "input_additional.add.xml", "-b", "0", "-e", "1000"], r"sumo\output\cross3ltl_inductloops"),
    (r"sumo\output\cross3ltl_inductloops", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--lateral-resolution", "0.8", "--no-step-log", "--no-duration-log", "--net-file=net.net.xml", "-r", "input_routes.rou.xml", "-a", "input_additional.add.xml", "-b", "0", "-e", "1000"], r"sumo\output\cross3ltl_inductloops"),
    (r"sumo\output\cross3ltl_meandata_constrained", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--no-step-log", "--no-duration-log", "--net-file=net.net.xml", "-r", "input_routes.rou.xml", "-a", "input_additional.add.xml", "-b", "0", "-e", "1000"], r"sumo\output\cross3ltl_meandata_constrained"),
    (r"sumo\output\cross3ltl_meandata_constrained", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--mesosim", "--no-step-log", "--no-duration-log", "--net-file=net.net.xml", "-r", "input_routes.rou.xml", "-a", "input_additional.add.xml", "-b", "0", "-e", "1000"], r"sumo\output\cross3ltl_meandata_constrained"),
    (r"sumo\output\cross3ltl_meandata_constrained", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--lateral-resolution", "0.8", "--no-step-log", "--no-duration-log", "--net-file=net.net.xml", "-r", "input_routes.rou.xml", "-a", "input_additional.add.xml", "-b", "0", "-e", "1000"], r"sumo\output\cross3ltl_meandata_constrained"),
    (r"sumo\output\cross3ltl_meandata_edges", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--no-step-log", "--no-duration-log", "--net-file=net.net.xml", "-r", "input_routes.rou.xml", "-a", "input_additional.add.xml", "-b", "0", "-e", "1000"], r"sumo\output\cross3ltl_meandata_edges"),
    (r"sumo\output\cross3ltl_meandata_edges", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--mesosim", "--no-step-log", "--no-duration-log", "--net-file=net.net.xml", "-r", "input_routes.rou.xml", "-a", "input_additional.add.xml", "-b", "0", "-e", "1000"], r"sumo\output\cross3ltl_meandata_edges"),
    (r"sumo\output\cross3ltl_meandata_edges", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--lateral-resolution", "0.8", "--no-step-log", "--no-duration-log", "--net-file=net.net.xml", "-r", "input_routes.rou.xml", "-a", "input_additional.add.xml", "-b", "0", "-e", "1000"], r"sumo\output\cross3ltl_meandata_edges"),
    (r"sumo\output\cross3ltl_meandata_lanes", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--no-step-log", "--no-duration-log", "--net-file=net.net.xml", "-r", "input_routes.rou.xml", "-a", "input_additional.add.xml", "-b", "0", "-e", "1000"], r"sumo\output\cross3ltl_meandata_lanes"),
    (r"sumo\output\cross3ltl_meandata_lanes", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--mesosim", "--no-step-log", "--no-duration-log", "--net-file=net.net.xml", "-r", "input_routes.rou.xml", "-a", "input_additional.add.xml", "-b", "0", "-e", "1000"], r"sumo\output\cross3ltl_meandata_lanes"),
    (r"sumo\output\cross3ltl_meandata_lanes", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--lateral-resolution", "0.8", "--no-step-log", "--no-duration-log", "--net-file=net.net.xml", "-r", "input_routes.rou.xml", "-a", "input_additional.add.xml", "-b", "0", "-e", "1000"], r"sumo\output\cross3ltl_meandata_lanes"),
    (r"sumo\output\cross3ltl_queue", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--no-step-log", "--no-duration-log", "--queue-output=queue.xml", "--net-file=net.net.xml", "-r", "input_routes.rou.xml", "-b", "0", "-e", "200"], r"sumo\output\cross3ltl_queue"),
    (r"sumo\output\cross3ltl_queue", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--mesosim", "--no-step-log", "--no-duration-log", "--queue-output=queue.xml", "--net-file=net.net.xml", "-r", "input_routes.rou.xml", "-b", "0", "-e", "200"], r"sumo\output\cross3ltl_queue"),
    (r"sumo\output\cross3ltl_queue", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--lateral-resolution", "0.8", "--no-step-log", "--no-duration-log", "--queue-output=queue.xml", "--net-file=net.net.xml", "-r", "input_routes.rou.xml", "-b", "0", "-e", "200"], r"sumo\output\cross3ltl_queue"),
    (r"sumo\output\cross3ltl_rawdump", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--no-step-log", "--no-duration-log", "--netstate-dump=rawdump.xml", "--net-file=net.net.xml", "-r", "input_routes.rou.xml", "-b", "90", "-e", "120"], r"sumo\output\cross3ltl_rawdump"),
    (r"sumo\output\cross3ltl_rawdump", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--mesosim", "--no-step-log", "--no-duration-log", "--netstate-dump=rawdump.xml", "--net-file=net.net.xml", "-r", "input_routes.rou.xml", "-b", "90", "-e", "120"], r"sumo\output\cross3ltl_rawdump"),
    (r"sumo\output\cross3ltl_rawdump", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--lateral-resolution", "0.8", "--no-step-log", "--no-duration-log", "--netstate-dump=rawdump.xml", "--net-file=net.net.xml", "-r", "input_routes.rou.xml", "-b", "90", "-e", "120"], r"sumo\output\cross3ltl_rawdump"),
    (r"sumo\output\cross3ltl_summary", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--no-step-log", "--no-duration-log", "--net-file=net.net.xml", "-r", "input_routes.rou.xml", "--summary=summary.xml", "-b", "0", "-e", "1000"], r"sumo\output\cross3ltl_summary"),
    (r"sumo\output\cross3ltl_summary", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--mesosim", "--no-step-log", "--no-duration-log", "--net-file=net.net.xml", "-r", "input_routes.rou.xml", "--summary=summary.xml", "-b", "0", "-e", "1000"], r"sumo\output\cross3ltl_summary"),
    (r"sumo\output\cross3ltl_summary", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--lateral-resolution", "0.8", "--no-step-log", "--no-duration-log", "--net-file=net.net.xml", "-r", "input_routes.rou.xml", "--summary=summary.xml", "-b", "0", "-e", "1000"], r"sumo\output\cross3ltl_summary"),
    (r"sumo\output\cross3ltl_tripinfo", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--no-step-log", "--no-duration-log", "--tripinfo-output=tripinfos.xml", "--net-file=net.net.xml", "-r", "input_routes.rou.xml", "-b", "0", "-e", "1000"], r"sumo\output\cross3ltl_tripinfo"),
    (r"sumo\output\cross3ltl_tripinfo", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--mesosim", "--no-step-log", "--no-duration-log", "--tripinfo-output=tripinfos.xml", "--net-file=net.net.xml", "-r", "input_routes.rou.xml", "-b", "0", "-e", "1000"], r"sumo\output\cross3ltl_tripinfo"),
    (r"sumo\output\cross3ltl_vehroutes", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--no-step-log", "--no-duration-log", "--vehroute-output=vehroutes.xml", "--net-file=net.net.xml", "-r", "input_routes.rou.xml", "-b", "0", "-e", "1000"], r"sumo\output\cross3ltl_vehroutes"),
    (r"sumo\output\cross3ltl_vehroutes", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--mesosim", "--no-step-log", "--no-duration-log", "--vehroute-output=vehroutes.xml", "--net-file=net.net.xml", "-r", "input_routes.rou.xml", "-b", "0", "-e", "1000"], r"sumo\output\cross3ltl_vehroutes"),
    (r"sumo\output\cross3ltl_vehroutes", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--lateral-resolution", "0.8", "--no-step-log", "--no-duration-log", "--vehroute-output=vehroutes.xml", "--net-file=net.net.xml", "-r", "input_routes.rou.xml", "-b", "0", "-e", "1000"], r"sumo\output\cross3ltl_vehroutes"),
    (r"sumo\output\cross3ltl_vtypeprobe", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--no-step-log", "--no-duration-log", "--net-file=net.net.xml", "-r", "input_routes.rou.xml", "-a", "input_additional.add.xml", "-b", "0", "-e", "220"], r"sumo\output\cross3ltl_vtypeprobe"),
    (r"sumo\output\cross3ltl_vtypeprobe", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--mesosim", "--no-step-log", "--no-duration-log", "--net-file=net.net.xml", "-r", "input_routes.rou.xml", "-a", "input_additional.add.xml", "-b", "0", "-e", "220"], r"sumo\output\cross3ltl_vtypeprobe"),
    (r"sumo\output\cross3ltl_vtypeprobe", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--lateral-resolution", "0.8", "--no-step-log", "--no-duration-log", "--net-file=net.net.xml", "-r", "input_routes.rou.xml", "-a", "input_additional.add.xml", "-b", "0", "-e", "220"], r"sumo\output\cross3ltl_vtypeprobe"),
    (r"sumo\simple_nets\cross\cross1ltl", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--time-to-teleport", "-1", "--no-step-log", "--no-duration-log", "--net-file=net.net.xml", "--routes=input_routes.rou.xml"], r"sumo\simple_nets\cross\cross1ltl"),
    (r"sumo\simple_nets\cross\cross1l", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--time-to-teleport", "-1", "-v", "--no-step-log", "--net-file=net.net.xml", "--routes=input_routes.rou.xml"], r"sumo\simple_nets\cross\cross1l"),
    (r"sumo\simple_nets\cross\cross1l", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--mesosim", "--meso-junction-control", "--time-to-teleport", "-1", "-v", "--no-step-log", "--net-file=net.net.xml", "--routes=input_routes.rou.xml"], r"sumo\simple_nets\cross\cross1l"),
    (r"sumo\simple_nets\cross\cross1l", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--lateral-resolution", "0.8", "--time-to-teleport", "-1", "-v", "--no-step-log", "--net-file=net.net.xml", "--routes=input_routes.rou.xml"], r"sumo\simple_nets\cross\cross1l"),
    (r"sumo\simple_nets\cross\cross3ltl", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--time-to-teleport", "-1", "--no-step-log", "--no-duration-log", "--net-file=net.net.xml", "--routes=input_routes.rou.xml"], r"sumo\simple_nets\cross\cross3ltl"),
    (r"sumo\simple_nets\cross\cross3l", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--time-to-teleport", "-1", "--no-step-log", "--no-duration-log", "--net-file=net.net.xml", "--routes=input_routes.rou.xml"], r"sumo\simple_nets\cross\cross3l"),
    (r"sumo\simple_nets\box\box1l", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--time-to-teleport", "-1", "--no-step-log", "--no-duration-log", "--net-file=net.net.xml", "--routes=input_routes.rou.xml"], r"sumo\simple_nets\box\box1l"),
    (r"sumo\simple_nets\box\box2l", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--time-to-teleport", "-1", "--no-step-log", "--no-duration-log", "--net-file=net.net.xml", "--routes=input_routes.rou.xml"], r"sumo\simple_nets\box\box2l"),
    (r"sumo\simple_nets\box\box3l", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--time-to-teleport", "-1", "--no-step-log", "--no-duration-log", "--net-file=net.net.xml", "--routes=input_routes.rou.xml"], r"sumo\simple_nets\box\box3l"),
    (r"sumo\simple_nets\box\box4l", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--time-to-teleport", "-1", "--no-step-log", "--no-duration-log", "--net-file=net.net.xml", "--routes=input_routes.rou.xml"], r"sumo\simple_nets\box\box4l"),
    (r"sumo\sublane_model", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--no-step-log", "--net-file=net.net.xml", "--routes=input_routes.rou.xml", "--lateral-resolution", "0.64", "--tripinfo-output", "tripinfos.xml", "--duration-log.statistics"], r"sumo\sublane_model"),
    (r"sumo\sublane_model", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--step-method.ballistic", "--no-step-log", "--net-file=net.net.xml", "--routes=input_routes.rou.xml", "--lateral-resolution", "0.64", "--tripinfo-output", "tripinfos.xml", "--duration-log.statistics"], r"sumo\sublane_model"),
    (r"sumo\model_railroad", [join(SUMO_HOME, "bin", "sumo"), "--write-license", "--default.speeddev", "0", "--railsignal-block-output", "railsignal_blocks.xml", "-c", "sumo.sumocfg", "-e", "3600"], r"sumo\model_railroad"),
    (r"tools\dua-iterate", [sys.executable, join(SUMO_HOME, "tools/assign/duaIterate.py"), "-n", "input_net.net.xml", "-t", "input_trips.trips.xml", "-l", "5"], r"tools\dua-iterate"),
    (r"tools\flowrouter", [sys.executable, join(SUMO_HOME, "tools/detector/flowrouter.py"), "-n", "input_net.net.xml", "-d", "input_detectors.det.xml", "-f", "input_flows.txt", "--verbose"], r"tools\flowrouter"),
    (r"tools\traceExporter", [sys.executable, join(SUMO_HOME, "tools/traceExporter.py"), "-i", "fcd.xml", "-n", "net.net.xml", "--ns2mobility-output", "mobilityfile.tcl"], r"tools\traceExporter"),
    (r"tutorial\circles", [sys.executable, "./runner.py"], r"../tutorial\circles"),
    (r"tutorial\city_mobil", [sys.executable, "./runner.py"], r"../tutorial\city_mobil"),
    (r"tutorial\hello", [sys.executable, "./runner.py"], r"../tutorial\hello"),
    (r"tutorial\manhattan", [sys.executable, "./runner.py"], r"../tutorial\manhattan"),
    (r"tutorial\output_parsing", [sys.executable, "./runner.py"], r"../tutorial\output_parsing"),
    (r"tutorial\quickstart", [sys.executable, "./runner.py"], r"../tutorial\quickstart"),
    (r"tutorial\sumolympics", [sys.executable, "./runner.py"], r"../tutorial\sumolympics"),
    (r"tutorial\traci_pedestrian_crossing", [sys.executable, "./runner.py", "--nogui"], r"../tutorial\traci_pedestrian_crossing"),
    (r"tutorial\traci_taxi", [sys.executable, "./runner.py"], r"../tutorial\traci_taxi"),
    (r"tutorial\traci_tls", [sys.executable, "./runner.py", "--nogui"], r"../tutorial\traci_tls"),
    (r"tutorial\public_transport", [sys.executable, "./runner.py"], r"../tutorial\public_transport"),
]
procs = []
def check():
    for d, p in procs:
        if p.wait() != 0:
            print("Error: '%s' failed for '%s'!" % (" ".join(getattr(p, "args", [str(p.pid)])), d))
            sys.exit(1)

for dir, call, wd in calls:
    procs.append((dir, subprocess.Popen(call, cwd=join(THIS_DIR, wd))))
    if len(procs) == multiprocessing.cpu_count():
        check()
        procs = []
check()