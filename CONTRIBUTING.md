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