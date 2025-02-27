##### Telegram: [Pelosi Watch](t.me/devfinanceros)
##### Donations are welcome [bontin.eth](app.ens.domains/bontin.eth)

# Watch Nancy Pelosi Stock Filings

### Set Up a Telegram Bot:
- Create a bot via Telegram’s BotFather to get a bot token (e.g., `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`).
- Add the bot to your Telegram channel as an administrator (so it can post messages and files).
- Get your channel’s ID (e.g., `@YourChannelName` or a numeric ID like `-123456789`). You can find it by sending a message to the bot in the channel or using `@get_id_bot` in Telegram.



1. Create a virtual env `python3 -m venv env`
2. Activate the virtual env `source env/bin/activate`
3. Install the requirements `pip install -r requirements.txt`
4. Create a `.env` file with the following content:
```
TELEGRAM_BOT_TOKEN='your_bot_token'
TELEGRAM_CHANNEL_ID='@your_channel_id'
```
5. Run the app `python3 __main__.py`
