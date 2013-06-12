XDM-main-plugin-repo
====================

The official main Plugin Repository for [https://github.com/lad1337/XDM](https://github.com/lad1337/XDM)<br>
Some basic Plugins you can found here.

The issue with this repo is that all plugins are downloaded on a single request.<br>
But that could be easily changed if the download url link to different zip files.<br>
This might be done later if plugins get big and alot.

Please feel free to use these plugins to create your own plugin(s).

DEV
===
<pre>
{
    "name": "name of your repo",
    "info_url": "url to some site that has information on yout repo",    
    "plugins": {
        "identifier.of.your.plugin": [
            {
                "major_version": 0, // the major version number X of "X.Y" the version in the plugin
                "minor_version": 2, // the minor version number Y of "X.Y" the version in the plugin
                "format": "zip", // right now only zip is suported
                "desc": "The description of your plugin",
                "name": "The name/screen name. IMPORTEND: this must be the same as the folder name in the zip",
                "type": "Notifier",
                "xdm_version": [ // minimal XDM version needed for this plugin since XDM Zim 0.4.16
                    0, 
                    4, 
                    16
                ], 
                "download_url": "download to the zip containing the plugin"
            }
        ]
    }
}
</pre>
See https://github.com/lad1337/XDM-main-plugin-repo/blob/master/meta.json for running example.<br>
**Please make sure your json is valid, check at [http://jsonlint.com/](http://jsonlint.com/)**
