from ROAR.agent_module.agent import Agent
from pathlib import Path
# from ROAR.control_module.stanley_controller import Stanley_controller
from ROAR.control_module.bstanley_controller import BStanley_controller
# from ROAR.control_module.cstanley_controller import CStanley_controller

from ROAR.control_module.pid_controller import PIDController
from ROAR.planning_module.local_planner.simple_waypoint_following_local_planner import \
    SimpleWaypointFollowingLocalPlanner
from ROAR.planning_module.behavior_planner.behavior_planner import BehaviorPlanner
from ROAR.planning_module.mission_planner.waypoint_following_mission_planner import WaypointFollowingMissionPlanner
from ROAR.utilities_module.data_structures_models import SensorsData
from ROAR.utilities_module.vehicle_models import VehicleControl, Vehicle
import logging


class JAM3Agent(Agent):
    def __init__(self, target_speed=120, **kwargs):
        super().__init__(**kwargs)
        self.target_speed = target_speed
        self.logger = logging.getLogger("Stanley Agent")
        self.route_file_path = Path(self.agent_settings.waypoint_file_path)
        #self.pid_controller = PIDController(agent=self, steering_boundary=(-1, 1), throttle_boundary=(-1, 1))
        self.bstanley_controller = BStanley_controller(agent=self, steering_boundary=(-1, 1), throttle_boundary=(-1, 1))
        #self.cstanley_controller = CStanley_controller(agent=self, steering_boundary=(-1, 1), throttle_boundary=(-1, 1))

        self.mission_planner = WaypointFollowingMissionPlanner(agent=self)
        # initiated right after mission plan

        self.behavior_planner = BehaviorPlanner(agent=self)
        self.local_planner = SimpleWaypointFollowingLocalPlanner(
            agent=self,
            controller=self.bstanley_controller,
            #controller=self.cstanley_controller,

            mission_planner=self.mission_planner,
            behavior_planner=self.behavior_planner,
            closeness_threshold=1)
        self.logger.debug(
            f"Waypoint Following Agent Initiated. Reading f"
            f"rom {self.route_file_path.as_posix()}")

    def run_step(self, vehicle: Vehicle,
                 sensors_data: SensorsData) -> VehicleControl:
        super(JAM3Agent, self).run_step(vehicle=vehicle,
                                       sensors_data=sensors_data)
        self.transform_history.append(self.vehicle.transform)
        if self.local_planner.is_done():
            control = VehicleControl()
            self.logger.debug("Path Following Agent is Done. Idling.")
        else:
            control = self.local_planner.run_in_series()
        return control