# WakabaMiko
Let us all strive to be virtuous souls together.

## About
Second bot for Twitch, focusing on a user interaction system called "Faith and 
Virtue". Basically, a way of mediating rewards based on both individual behaviour and overall chat behaviour and activity. WakabaMiko currently implements v1.0.0 of Faith and Virtue.

## Faith and Virtue v1.0.0
Currently, the system has one output: blessings, and one input: chat messages. Penalty terms may apply a virtue penalty, a faith penalty, or both. Bonus terms will apply a virtue bonus. Messages that do neither will, by default, generate virtue. The total values of these are used to determine the chances of getting specific blessings.

## Dependencies
[GetterCore library](https://github.com/sym-okami/GetterCore)\
Python 3.6+

## bot_auth.json format
The superobot_wrapper expects a file named bot_auth.json to be placed in the 
same directory. The contents should be structured as such:
```
{
    "user": "{twitchUserName}",
    "oauth": "oauth:{oauthKey}",
    "channels": ["#{channel1}", "#{channel2}"]
}
```
where anything within the curly braces should be replaced with the appropriate 
values.

## Links
[My Twitch](https://www.twitch.tv/symulacra)\
[Wakaba Miko's Twitch](https://www.twitch.tv/wakaba_miko)