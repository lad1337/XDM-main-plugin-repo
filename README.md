XDM-main-plugin-repo
====================

The official main Plugin Repository.
Some basic Plugins you can found here.

The issue with this repo is that all plugins are downloaded on a single request.
But that could be easily changed if the download url link to different zip files.
This might be done later if plugins get big and alot.

DEV
===
<pre>
{
    "name": "name of your repo",
    "plugins": {
        "identifier.of.your.plugin": [
            {
                "major_version": 0, // the major version number X of "X.Y" the version in the plugin
                "minor_version": 2, // the minor version number Y of "X.Y" the version in the plugin
                "format": "zip", // right now only zip is suported
                "desc": "The description of your plugin",
                "name": "The name/screen name. IMPORTEND: this must be the same as the folder name in the zip",
                "type": "Notifier",
                "info_url": "url to some site that has information on yout repo",
                "update_url": "url to this json must be raw link on github",
                "download_url": "download to the zip containing the plugin"
            }
        ]
    }
}
</pre>
See https://github.com/lad1337/XDM-main-plugin-repo/blob/master/meta.json for running example
please make sure your json is valid, check at http://jsonlint.com/