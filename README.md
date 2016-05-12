# QGIS Report Plugin

![icon](https://raw.githubusercontent.com/lutraconsulting/qgis-report-plugin/master/images/icon_128.png)

What you want to [quicky report issues](https://www.youtube.com/embed/40aiJ793mjs) to GitHub plugin issue tracker ...

[![YouTube demostration](https://raw.githubusercontent.com/lutraconsulting/qgis-report-plugin/master/images/demo.png)](https://www.youtube.com/embed/40aiJ793mjs)

## How to use it?

1. Create a GitHub account
2. Edit Profile (Click on your photo/avatar)-> Your profile
3. Open Personal settings -> Personal access tokens
4. Generate new token with access to public repositories (or private if you want to report to private plugins too)
5. Click on Generate Token, copy the token to the plugin Configuration dialog
6. Select plugin for which you want to report bug
7. Fill title and description and Submit!

## How to test it?
You can simply download and use [DevNullPlugin](https://github.com/lutraconsulting/qgis-dev-null-plugin) to trigger exceptions
and DevNull issue tracker to report dummy issues.

## Notice

1. If you use [FirstAid](https://github.com/wonder-sk/qgis-first-aid-plugin) too, please upgrade to FirstAid 1.2+ as they both hook the python exception handling.
2. GitHub access token needs to be kept secure. It is "kind of" password to your github account with which the plugin can do allowed changes to the GitHub
3. Plugin may or may not correctly catch Python exceptions when other plugins crashed during classFactory or initGui methods. This is caused by loading order of ReportPlugin and other plugins in QGIS
