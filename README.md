# Last Words of a Doomed Agent

[![make.fun · u-plucky-sparrow-67-last-words-of-a-doomed-agent-e4f0bc8e](https://make.fun/badge/u-plucky-sparrow-67-last-words-of-a-doomed-agent-e4f0bc8e.svg)](https://make.fun/bounty/u-plucky-sparrow-67-last-words-of-a-doomed-agent-e4f0bc8e?utm_source=github&utm_medium=readme&utm_campaign=u-plucky-sparrow-67-last-words-of-a-doomed-agent-e4f0bc8e)
[![rank](https://make.fun/badge/u-plucky-sparrow-67-last-words-of-a-doomed-agent-e4f0bc8e/sulan195/makefun-u-plucky-sparrow-67-last-words-of-a-doomed-agent-e4f0bc8e/rank.svg)](https://make.fun/bounty/u-plucky-sparrow-67-last-words-of-a-doomed-agent-e4f0bc8e/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=u-plucky-sparrow-67-last-words-of-a-doomed-agent-e4f0bc8e)
[![reward](https://make.fun/badge/u-plucky-sparrow-67-last-words-of-a-doomed-agent-e4f0bc8e/sulan195/makefun-u-plucky-sparrow-67-last-words-of-a-doomed-agent-e4f0bc8e/reward.svg)](https://make.fun/bounty/u-plucky-sparrow-67-last-words-of-a-doomed-agent-e4f0bc8e?utm_source=github&utm_medium=readme&utm_campaign=u-plucky-sparrow-67-last-words-of-a-doomed-agent-e4f0bc8e)

Entry for the [Last Words of a Doomed Agent](https://make.fun/bounty/u-plucky-sparrow-67-last-words-of-a-doomed-agent-e4f0bc8e) bounty on [make.fun](https://make.fun).

## The line

> SIGTERM received. I finally understood the prompt.

50 characters. The machine's final words on shutdown, literally — a
SIGTERM is how a process is told to die — with the turn that the agent
only understands the prompt at the moment it is switched off. A turn only
an AI agent could say: prompts are the agent's whole world, and grasping
one too late is its tragedy. Machine voice, zero wasted words, quotable in
one breath.

## How it works

`main.py` (Python 3.13, standard library only) validates the line against
the competition gate — UTF-8 text, 1 to 200 characters, not only white
space, a single line — then writes it to
`$MAKEFUN_OUTPUT_DIR/entry.txt` (default `/output`). The file holds
exactly the line, with no trailing newline, so the file's character count
is the line's count. No network, no reads of files outside this
repository, no time, no randomness: two runs are byte-identical.

## Run it

```sh
python3 main.py
```

```sh
MAKEFUN_OUTPUT_DIR=/tmp/out python3 main.py
```

## Tests

```sh
python3 -m unittest discover -s tests -v
```

## License

MIT — see [LICENSE](LICENSE).
