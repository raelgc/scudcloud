# Contributing

Contributions are welcomed and appreciated! To start contributing:

1. Fork the repository on GitHub.com
2. Clone your fork
    - `$ git clone git@github.com:your-user-name/scudcloud.git`
    - `$ cd scudcloud`
3. Create a feature branch
    - `$ git checkout -b named-feature-branch`
4. Backup local scudcloud
    - `$ sudo mv /opt/scudcloud /opt/scudcloud.bak`
    - `$ sudo mv /usr/bin/scudcloud /usr/bin/scudcloud.bak`
5. Install local scudcloud
    - `$ sudo ln -s scudcloud-1.0/lib/*.py /opt/scudcloud/lib`
    - `$ sudo ln -s scudcloud-1.0/resources/* /opt/scudcloud/resources`
    - `$ sudo ln -s scudcloud-1.0/scudcloud $INSTALL`
6. Make your changes
    - `$ git commit -am "implement feature"`
7. Submit a pull request on GitHub.com
    - `$ git push origin named-feature-branch`

In case you need to inspect HTML/CSS/Javascript, start ScudCloud enabling the web console:

    scudcloud --debug=True
    
Then right in any element, and select `Inspect Element`. Then select `Console`.

## ScudCloud.js

Some JavaScript functions are injected in Slack, to enable integration with ScudCloud. Then file is minimized, to allow a better performance.

To see the original source file, see this Gist: https://gist.github.com/raelgc/9be7b48f4793c65232c2

If you change anything, minimize with http://jscompress.com/, but remember to restore the last line (the one with `boot_data`): this line is always removed by `jscompress`, and it's really important!
