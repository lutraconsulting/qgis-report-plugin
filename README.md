# QGIS Report Plugin

![icon](https://raw.githubusercontent.com/lutraconsulting/qgis-report-plugin/master/images/icon_128.png)

What you want to quicky report issues to GitHub plugin issue tracker..

## How to use it?

1. Create a GitHub account
2. Edit Profile (Click on your photo/avatar)-> Your profile
3. Open Personal settings -> Personal access tokens
4. Generate new token with access to public repositories (or private if you want to report to private plugins too)
5. Click on Generate Token, copy the token to the plugin
6. Select plugin for which you want to report bug
7. Fill title and description and Submit!

## Notice

1. It may not use with [FirstAid](https://github.com/wonder-sk/qgis-first-aid-plugin) as they both hook the python exception handling. If you need both simultanously you can use [plugin reloader](https://github.com/borysiasty/plugin_reloader) to reload Report Plugin after start of QGIS. See [issue 21](https://github.com/lutraconsulting/qgis-report-plugin/issues/21)
2. GitHub access token needs to be kept secure. It is "kind of" password to your github account with which the plugin can do allowed changes to the github
3. Plugin may not work at all when other plugin crashed during classFactory or initGui methods. This is caused by loading order of ReportPlugin and other plugins by QGIS
