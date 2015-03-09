# skyline

#### Table of Contents

1. [Overview](#overview)
2. [Module Description - What the module does and why it is useful](#module-description)
3. [Setup - The basics of getting started with skyline](#setup)
    * [What skyline affects](#what-skyline-affects)
    * [Setup requirements](#setup-requirements)
    * [Beginning with skyline](#beginning-with-skyline)
4. [Usage - Configuration options and additional functionality](#usage)
5. [Reference - An under-the-hood peek at what the module is doing and how](#reference)
5. [Limitations - OS compatibility, etc.](#limitations)
6. [Development - Guide for contributing to the module](#development)

## Overview

Automatically installs redis, all python modules required by skyline, and skyline itself.

## Module Description

This module installs skyline on a server as well as provides the ability to completely automate the configuration and startup of each service required by skyline

If your module has a range of functionality (installation, configuration,
management, etc.) this is the time to mention it.

## Setup

### What skyline affects


  # OS Package installs
  - python-pip
  - hiredis
  - python-devel
  - python-daemon
  - python-simplejson
  - python-unittest2
  - python-mock
  - gcc
  - blas
  - blas-devel
  - lapack-devel 
  - gcc-c++
  
  # Python (pip) packages
  - numpy
  - scipy
  - pandas
  - patsy
  - jinja2
  - flask
  - itsdangerous
  - werkzeug
  - markupsafe
  - pytz
  - python-dateutil
  - six
  - statsmodels
  - msgpack-python

  # Adds files
  - /etc/init.d/skyline-horizon
  - /etc/init.d/skyline-analyzer
  - /etc/init.d/skyline-webapp
  - All skyline binaries in the path specified during install

  # Template files
  - Skyline configuration (settings.py)
  - Skyline Analyzer init (skyline-analyzer)
  - Skyline Horizon init (skyline-horizon)
  - Skyline Webapp init (skyline-webapp)

### Beginning with skyline

Simply assign the skyline class to the system you are provisioning. All defaults are already provided and should bring up a successful installation without parameters for the class, needed.
Default install path is /opt

## Usage
  
 # Confiruation option defaults

  - $username           = 'skyline',
  - $group              = 'skyline',
  - $install_dir        = '/opt',
  - $download_url       = 'https://github.com/etsy/skyline/archive/master.zip',
  - $redis_socket_path  = '/tmp/redis.sock',
  - $log_path           = '/var/log/skyline',
  - $pid_path           = '/var/run/skyline',
  - $dump_dir           = '/var/dump',
  - $full_namespace     = 'metrics.',
  - $mini_namespace     = 'mini.',
  - $full_duration      = 86400,
  - $mini_duration      = 3600,
  - $graphite_host      = 'your_graphite_host.com',
  - $graphite_url       = "http://' + GRAPHITE_HOST + '/render/?width=1400&from=-1hour&target=%s",
  - $carbon_port        = 2003,
  - $oculus_host        = 'http://you_oculus_host.com',
  - $anomaly_dump       = 'webapp/static/dump/anomalies.json',
  - $analyzer_processes = 7,
  - $stale_period       = 500,
  - $min_tolerable_length = 1,
  - $max_tolerable_boredom = 100,
  - $boredom_set_size   = 1,
  - $canary_metric      = 'statsd.numStats',
  - $consensus          = 6,
  - $enable_second_order = 'False',
  - $enable_alerts      = 'True',
  - $horizon_ip         = '0.0.0.0',
  - $worker_processes   = 2,
  - $pickle_port        = 2024,
  - $udp_port           = 2025,
  - $chunk_size         = 10,
  - $max_queue_size     = 500,
  - $roomba_processes   = 1,
  - $roomba_grace_time  = 600,
  - $max_resolution     = 1000,
  - $webapp_ip          = '0.0.0.0',
  - $webapp_port        = 1500,
  - $skip_list          = [
                         '',
                        ],
  - $algorithms         = [
                         'first_hour_average',
                         'mean_subtraction_cumulation',
                         'stddev_from_average',
                         'stddev_from_moving_average',
                         'least_squares',
                         'grubbs',
                         'histogram_bins',
                         'median_absolute_deviation',
                         'ks_test',
                        ],
  - $alerts             = [
                         '("skyline", "smtp", 1800),'
                        ],
  - $hipchat_opts       = [
                         '"rooms": { "skyline": (12345,),},', 
                         '"color": "purple",'
                        ],
  - $smtp_opts          = [
                         '"sender": "skyline-alerts@etsy.com",',
                         '"recipients": {"skyline":["email@address.com", "email2@address.com"],},'
                        ],
  - $pagerduty_opts     = [
                         '"subdomain": "example",',
                         '"auth_token": "key",',
                         '"key": "key",',
                        ],

## Reference

Built on fsalum/redis and gini/archive

## Limitations

This module has currently only been tested on RHEL systems. Inclusions were made so that the module should work on any linux distro, but this hasn't been tested.

## Development

If you find bugs, please post back to my issues page on github.
https://github.com/HawtDogFlvrWtr/puppet-skyline/issues

Contributions welcome and all submissions will be merged if found to compile correctly and are seen as useful.

