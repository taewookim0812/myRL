from pybulletgym.envs.roboschool.envs.env_bases import BaseBulletEnv
from pybulletgym.envs.roboschool.scenes.scene_bases import SingleRobotEmptyScene
from assets.robots.robot_bases import URDFBasedRobot
import numpy as np
import operator
from utils.utils import *


class Mirobot(URDFBasedRobot):
    TARG_LIMIT = deg2rad(15)

    def __init__(self):
        URDFBasedRobot.__init__(self, model_urdf='mirobot_description\mirobot.urdf', robot_name='mirobot_urdf', action_dim=8, obs_dim=6)
        print("Pybullet-Mirobot class description")

    def robot_specific_reset(self, physicsClient):
        print("jdict: ", self.jdict)
        print("parts: ", self.parts)
        self.j1 = self.jdict["joint1"]
        self.j2 = self.jdict["joint2"]
        self.j3 = self.jdict["joint3"]
        self.j4 = self.jdict["joint4"]
        self.j5 = self.jdict["joint5"]
        self.j6 = self.jdict["joint6"]
        self.jlfinger = self.jdict["left_finger_joint"]
        self.jrfinger = self.jdict["right_finger_joint"]
        self.grip = 0

        self.j1.reset_current_position(np.random.uniform(low=-self.TARG_LIMIT, high=self.TARG_LIMIT), 0)
        self.j2.reset_current_position(np.random.uniform(low=-self.TARG_LIMIT, high=self.TARG_LIMIT), 0)
        self.j3.reset_current_position(np.random.uniform(low=-self.TARG_LIMIT, high=self.TARG_LIMIT), 0)
        self.j4.reset_current_position(np.random.uniform(low=-self.TARG_LIMIT, high=self.TARG_LIMIT), 0)
        self.j5.reset_current_position(np.random.uniform(low=-self.TARG_LIMIT, high=self.TARG_LIMIT), 0)
        self.j6.reset_current_position(np.random.uniform(low=-self.TARG_LIMIT, high=self.TARG_LIMIT), 0)
        self.jlfinger.reset_current_position(0.017, 0)
        self.jrfinger.reset_current_position(0.017, 0)

        self.phand = self.parts["mirobot_hand"]
        self.pleft_finger = self.parts["left_finger"]
        self.pright_finger = self.parts["right_finger"]

        finger_tip_pose = self.get_finger_tip_pose()
        self.draw_coordinate(origin=finger_tip_pose[:3], quat=finger_tip_pose[3:])

    def apply_action(self, a):
        assert (np.isfinite(a).all())
        self.j1.set_motor_torque(0.05 * float(np.clip(a[0], -1, +1)))
        self.j2.set_motor_torque(0.05 * float(np.clip(a[1], -1, +1)))
        self.j3.set_motor_torque(0.05 * float(np.clip(a[2], -1, +1)))
        self.j4.set_motor_torque(0.05 * float(np.clip(a[3], -1, +1)))
        self.j5.set_motor_torque(0.05 * float(np.clip(a[4], -1, +1)))
        self.j6.set_motor_torque(0.05 * float(np.clip(a[5], -1, +1)))
        self.grip = a[-1]
        grip_act = 0 if self.grip else 0.017
        self.jlfinger.set_position(grip_act)
        self.jrfinger.set_position(grip_act)

    def calc_state(self):
        theta1, theta_dot1 = self.j1.current_relative_position()
        theta2, theta_dot2 = self.j2.current_relative_position()
        theta3, theta_dot3 = self.j3.current_relative_position()
        theta4, theta_dot4 = self.j4.current_relative_position()
        theta5, theta_dot5 = self.j5.current_relative_position()
        theta6, theta_dot6 = self.j6.current_relative_position()
        return np.array([
            theta1, theta_dot1,
            theta2, theta_dot2,
            theta3, theta_dot3,
            theta4, theta_dot4,
            theta5, theta_dot5,
            theta6, theta_dot6,
            self.grip
        ])
        # theta, self.theta_dot = self.central_joint.current_relative_position()
        # self.gamma, self.gamma_dot = self.elbow_joint.current_relative_position()
        # target_x, _ = self.jdict["target_x"].current_position()
        # target_y, _ = self.jdict["target_y"].current_position()
        # self.to_target_vec = np.array(self.fingertip.pose().xyz()) - np.array(self.target.pose().xyz())
        # return np.array([
        #     target_x,
        #     target_y,
        #     self.to_target_vec[0],
        #     self.to_target_vec[1],
        #     np.cos(theta),
        #     np.sin(theta),
        #     self.theta_dot,
        #     self.gamma,
        #     self.gamma_dot,
        # ])

    def calc_potential(self):
        pass

    def get_finger_tip_pose(self):
        lfinger_pose = self.pleft_finger.get_pose()
        rfinger_pose = self.pright_finger.get_pose()
        center = 0.5 * (lfinger_pose[:3] + rfinger_pose[:3])
        m = quat_to_mat(lfinger_pose[3:])
        center += m[:, 2] * 0.023    # z-offset
        return np.concatenate((center, lfinger_pose[3:]), axis=0)

    def draw_coordinate(self, origin, quat, lenLine=0.1):
        mat = quat_to_mat(quat)
        px = origin + lenLine * mat[:, 0]
        py = origin + lenLine * mat[:, 1]
        pz = origin + lenLine * mat[:, 2]
        self._p.addUserDebugLine(origin, px, lineColorRGB=[1, 0, 0], lineWidth=2.0, lifeTime=0)
        self._p.addUserDebugLine(origin, py, lineColorRGB=[0, 1, 0], lineWidth=2.0, lifeTime=0)
        self._p.addUserDebugLine(origin, pz, lineColorRGB=[0, 0, 1], lineWidth=2.0, lifeTime=0)


class MirobotBulletEnv(BaseBulletEnv):
    def __init__(self):
        self.robot = Mirobot()
        BaseBulletEnv.__init__(self.robot)

    def create_single_player_scene(self, bullet_client):
        return SingleRobotEmptyScene(bullet_client, gravity=0.0, timestep=0.0165, frame_skip=1)

    def step(self, a):
        assert (not self.scene.multiplayer)
        self.robot.apply_action(a)
        self.scene.global_step()

        state = self.robot.calc_state()  # sets self.to_target_vec

        potential_old = self.potential
        self.potential = self.robot.calc_potential()

        electricity_cost = (
                -0.10 * (np.abs(a[0] * self.robot.theta_dot) + np.abs(
            a[1] * self.robot.gamma_dot))  # work torque*angular_velocity
                - 0.01 * (np.abs(a[0]) + np.abs(a[1]))  # stall torque require some energy
        )
        stuck_joint_cost = -0.1 if np.abs(np.abs(self.robot.gamma) - 1) < 0.01 else 0.0
        self.rewards = [float(self.potential - potential_old), float(electricity_cost), float(stuck_joint_cost)]
        self.HUD(state, a, False)
        return state, sum(self.rewards), False, {}

    def camera_adjust(self):
        x, y, z = self.robot.get_finger_tip_pose()[:3]
        x *= 0.5
        y *= 0.5
        self.camera.move_and_look_at(0.3, 0.3, 0.3, x, y, z)