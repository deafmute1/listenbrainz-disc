# listenbrainz-disc 
listenbrainz-disc (lbz) is a discord bot for accesing your listenbrainz scobbles, similar to [.fmbot](https://fmbot.xyz/) or [Chuu](https://github.com/ishwi/Chuu) for lastfm. 

## COPYRIGHT
This software is licensed under the terms defined in the file LICENSE.

## Public instance
I host a public instance on my home server. You can invite it at: 

## Data storage 
This application can store the following data on disk: 
  - If user runs !set_user:
    - Unique Discord Accont ID
    - Listenbrainz plaintext public username

- If you are using my own hosted instance of this bot, you can request deletion of your data at ethan@ethandjeric.com.

## Installation 
You can use the docker image, provided prebuilt as `deafmute/listenbrainz-disc` at [docker hub](https://hub.docker.com/repository/docker/deafmute/listenbrainz-disc). 
The only option the image requires (other than specify the image to run, of course...) is to set `LBZ_TOKEN` under `environment`. 
You also probably want to persist the app data by mounting `/data` somewhere.

Or, to run bare metal (using a virtual environment - you can do it without it too):
  1. `git clone https://github.com/deafmute1/listenbrainz-disc && cd listenbrainz-disc`
  2. `python -m venv env && source env/bin/activate`
  3. `pip install .` (does not install optional requirements like python-dotenv. Use `pip install -r requirements.txt && pip install .` for 1:1 match to development environment)
  4. `export LBZ_DISCORD_TOKEN=<secret>`
  5. `lbz` 
   
You must set the `LBZ_DISCORD_TOKEN` variable in the environment. This program optionally supports `.env` files via `python-dotenv`, if you install that. 

Further variables you can set (with their defaults):
  - 'LBZ_LOG_LEVEL': 'WARNING',
    'LBZ_LOG_FORMAT': '%(asctime)s : %(levelname)s : %(message)s',
    'LBZ_LOG_FILE': None,
    'LBZ_BOT_PREFIX': '!',
    'LBZ_MODE': 'EMBED',
    'LBZ_DATA_DIR': '.'

## TODO (somewhat ordered by prority)
- Improve/fix cover art looku (its pretty broken if it cant get a musicbrainz id from the listen object right now)
- Get youtube links for current track
- Some nice listenbrainz data collage/format commands, get top albums, tracks, genres whatever
  - Server wide stats?
  - Users listen per day
- Get user reccomendations
- Get lyrics for songs (support at _least_ Genius)
- Add logging
- Allow scrobbling (????, would require listenbrainz auth)
  - playback ???
