import torch
# import gym
# import pybulletgym
from task.task_desc import WrapperVecEnv
from utils.env_parse import get_pybulletgym_env_list
from utils.env_parse import make_env
from stable_baselines3 import A2C, PPO, SAC
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv, VecNormalize


def train_test():
    env_list = get_pybulletgym_env_list()
    env_name = env_list['PYBULLET_GYM_ENV_LIST'][8]
    device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
    env = WrapperVecEnv(env_name=env_name, num_envs=2, device=device, normalized_env=False)
    # n_procs = 2
    # env = DummyVecEnv([make_env(env_id=env_name, rank=i) for i in range(n_procs)])
    # env = VecNormalize(env)
    print("env: ", env)
    obs = env.reset()
    print("obs: ", obs.shape)
    for i in range(10):
        action = env.sample_action()
        obs, rew, _, _ = env.step(action)
        print("obs: ", obs)

    env.close()
    exit()
    env = gym.make(env_name)

    model = PPO('MlpPolicy', env, verbose=1)
    model.learn(total_timesteps=5000)

    env.render()
    obs = env.reset()
    for i in range(5000):
        action, _state = model.predict(obs, deterministic=True)
        obs, reward, done, info = env.step(action)
        # env.render()
        if done:
            obs = env.reset()


if __name__ == '__main__':
    train_test()