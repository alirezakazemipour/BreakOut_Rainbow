import gym
from logger import LOG
from play import Play
from agent import Agent
from utils import *

ENV_NAME = "Breakout-v0"
MAX_EPISODES = 20
MAX_STEPS = 1000
save_interval = 200
log_interval = 1  # TODO has conflicts with save interval when loading for playing is needed

episode_log = LOG()

TRAIN = True

if __name__ == '__main__':

    env = gym.make(ENV_NAME)
    n_actions = env.action_space.n
    stacked_frames = np.zeros(shape=[84, 84, 4], dtype='float32')
    agent = Agent(n_actions=n_actions,
                  gamma=0.99,
                  lr=6.25e-5,
                  tau=0.001,
                  state_shape=[84, 84, 4],
                  capacity=10000,
                  alpha=0.99,
                  epsilon_start=0.9,
                  epsilon_end=0.05,
                  epsilon_decay=200,
                  batch_size=32)
    if TRAIN:

        for episode in range(1, MAX_EPISODES + 1):
            s = env.reset()
            stacked_frames = stack_frames(stacked_frames, s, True)
            episode_reward = 0
            episode_loss = 0

            episode_log.on()

            for step in range(1, MAX_STEPS + 1):

                stacked_frames_copy = stacked_frames.copy()
                action = agent.choose_action(stacked_frames_copy)
                s_, r, d, _ = env.step(action)
                stacked_frames = stack_frames(stacked_frames, s_, False)
                r = np.clip(r, -1.0, 1.0)
                agent.store(stacked_frames_copy, action, r, stacked_frames, d)
                # env.render()
                if step % 4 == 0:
                    loss = agent.train()
                    episode_loss += loss
                else:
                    episode_loss += 0
                episode_reward += r

                # if step % save_interval == 0:
                #     episode_log.save_weights(agent.eval_model, agent.optimizer, episode, step)

                if d:
                    break

            episode_log.off()
            if episode % log_interval == 0:
                episode_log.printer(episode, episode_reward, episode_loss, agent.eps_threshold, step)
            # print(f'episode: {episode}. reward: {episode_reward}. loss: {episode_loss}')
    else:
        episode = MAX_EPISODES
        step = MAX_STEPS
        # region play
        play_path = "./models/" + episode_log.dir + "/" "episode" + str(episode) + "-" + "step" + str(step)
        player = Play(agent, env, play_path)
        player.evaluate()
        # endregion
