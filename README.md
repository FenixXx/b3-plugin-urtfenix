UrT Fenix Plugin for BigBrotherBot
==================================

BigBrotherBot plugin which allows to take benefits from the custom **ioQ3 1.35 urt-fenix** server engine.
Not that this plugin will work only with the above specified engine: if you are using another server engine, unload this plugin or your b3 will fail to start.

## How to install

### Installing the plugin

* Copy **urtfenix.py** into **b3/extplugins**
* Copy **plugin_urtfenix.ini** into **b3/extplugins/conf**
* Load the plugin in your **b3.xml** configuration file

### Requirements

In order to use this plugins you need to have b3 1.10-dev installed: http://files.cucurb.net/b3/daily/.<br>
You need to have a b3 version released after the 21st December 2013: the plugin makes use of several changes provided in the *plugin.py* module which are available since this release date.<br>

## In-game user guide

* **!radio &lt;on|off&gt;** *turn on|off the radio on the server*
* **!teleport &lt;client&gt;** *teleport yourself to another client*

## Support

For support regarding this very plugin you can find me on IRC on **#goreclan** @ **Quakenet**<br>
For support regarding Big Brother Bot you may ask for help on the official website: http://www.bigbrotherbot.net