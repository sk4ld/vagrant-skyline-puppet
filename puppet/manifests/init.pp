# == Class: skyline
#
# Skyline is a real-time* anomaly detection* system*, built to enable passive monitoring of hundreds of thousands of metrics, without the need to configure a model/thresholds for each one, as you might do with Nagios. It is designed to be used wherever there are a large quantity of high-resolution timeseries which need constant monitoring. Once a metrics stream is set up (from StatsD or Graphite or other source), additional metrics are automatically added to Skyline for analysis. Skyline's easily extendible algorithms automatically detect what it means for each metric to be anomalous. After Skyline detects an anomalous metric, it surfaces the entire timeseries to the webapp, where the anomaly can be viewed and acted upon.
# https://github.com/etsy/skyline
#
# === Parameters
#
# Document parameters here.
#
# [*sample_parameter*]
#   Explanation of what this parameter affects and what it defaults to.
#   e.g. "Specify one or more upstream ntp servers as an array."
#
# === Variables
#
# Here you should define a list of variables that this module would require.
#
# [*sample_variable*]
#   Explanation of how this variable affects the funtion of this class and if
#   it has a default. e.g. "The parameter enc_ntp_servers must be set by the
#   External Node Classifier as a comma separated list of hostnames." (Note,
#   global variables should be avoided in favor of class parameters as
#   of Puppet 2.6.)
#
# === Examples
#
#  class { 'skyline':
#    servers => [ 'pool.ntp.org', 'ntp.local.company.com' ],
#  }
#
# === Authors
#
# Christopher Phipps <hawtdogflvrwtr@gmail.com>
#
# === Copyright
#
# Copyright 2014 Your name here, unless otherwise noted.
#
# Reference params file for configuration variables
#
#  Requires gini/archive & fsalum/redis modules.
#
# === EXAMPLE
class { '::skyline':
  #download_url => 'HTTP://URL',
  #install_dir =>  '/home/vagrant/skyline/',
}


class skyline (
  $username           = 'skyline',
  $group              = 'skyline',
  $install_dir        = '/opt',
  $download_url       = 'https://github.com/etsy/skyline/archive/master.zip',
  $redis_socket_path  = '/tmp/redis.sock',
  $log_path           = '/var/log/skyline',
  $pid_path           = '/var/run/skyline',
  $dump_dir           = '/var/dump',
  $full_namespace     = 'metrics.',
  $mini_namespace     = 'mini.',
  $full_duration      = 86400,
  $mini_duration      = 3600,
  $graphite_host      = '192.168.1.100',
  $graphite_url       = "http://' + GRAPHITE_HOST + '/render/?width=1400&from=-1hour&target=metrics.%s",
  $carbon_port        = 2003,
  $oculus_host        = '',
  $anomaly_dump       = 'webapp/static/dump/anomalies.json',
  $analyzer_processes = 7,
  $stale_period       = 5000,
  $min_tolerable_length = 1,
  $max_tolerable_boredom = 1000,
  $boredom_set_size   = 1,
  $canary_metric      = 'statsd.numStats',
  $consensus          = 4,
  $enable_second_order = 'False',
  $enable_alerts      = 'True',
  $horizon_ip         = '0.0.0.0',
  $worker_processes   = 2,
  $pickle_port        = 2024,
  $udp_port           = 2025,
  $chunk_size         = 10,
  $max_queue_size     = 500,
  $roomba_processes   = 1,
  $roomba_grace_time  = 500000,
  $max_resolution     = 100000,
  $webapp_ip          = '0.0.0.0',
  $webapp_port        = 1500,
  $skip_list          = [
						'example.statsd.metric',
						'another.example.metric',
						],

  $algorithms         = [
                         'first_hour_average',
                         'mean_subtraction_cumulation',
                         'stddev_from_average',
                         'stddev_from_moving_average',
                         'least_squares',
                         #'grubbs',
                         #'histogram_bins',
                         'median_absolute_deviation',
                         #'ks_test',
                        ],
  $alerts             = [
                         '("skyline", "smtp", 1800),'
                        ],
  $hipchat_opts       = [
                         '"rooms": { "skyline": (12345,),},', 
                         '"color": "purple",'
                        ],
  $smtp_opts          = [
                         '"sender": "skyline-alerts@etsy.com",',
                         '"recipients": {"skyline":["email@address.com", "email2@address.com"],},'
                        ],
  $pagerduty_opts     = [
                         '"subdomain": "example",',
                         '"auth_token": "key",',
                         '"key": "key",',
                        ],
) {
    include 'archive::prerequisites'
    include 'stdlib'

    # Install redis
    class { '::redis':
      system_sysctl => false
    }

    # Ensure packages installed
    $basepackages = ['python-pip','hiredis','python-devel','python-daemon','python-simplejson','python-unittest2','python-mock','gcc','blas','blas-devel','lapack-devel','gcc-c++']
    # Important python packages that need to be installed before the other packages.
    $pipimportant = ['numpy','scipy']
    $pippackages = ['pandas','patsy','jinja2','flask','itsdangerous','werkzeug','markupsafe','pytz','python-dateutil','six','statsmodels','msgpack-python']
    
    # Ensure all base and pip packages are installed.
    package { $basepackages:
      ensure => 'installed',
    }
    package { $pipimportant:
      ensure => 'installed',
      provider => 'pip',
      before => Package[$pippackages],
    }
    package { $pippackages:
      provider => 'pip',
      ensure => 'installed',
      require => [Package['python-pip'], Package['gcc'], Package['gcc-c++']],
    }
 
    # Have to manually install redis python module with exec because of puppet bug PUP-1073
    # http://tickets.puppetlabs.com/browse/PUP-1073
    exec { "redis-install":
       path => "/usr/bin:/usr/sbin:/bin",
       command => 'pip install redis',
       require => [Package['python-pip'], Package['gcc'], Package['gcc-c++']],
       unless => 'pip list | grep -c "redis"',
    }

    # Create user/group information
    user { $username:
      comment => 'Skyline service account',
      groups => 'redis',
      ensure => present,
      before => [Service['skyline-analyzer'],Service['skyline-horizon'],Service['skyline-webapp']],
    }

    # Archive module to extract the skyline zip file
    archive { 'skyline':
      ensure => present,
      url => $download_url,
      target => $install_dir,
      extension => 'zip',
      checksum => false,
      strip_components => 1,
    }

    # Variables for install
    $require_target = Archive['skyline']
    $config_py = "${install_dir}/skyline/skyline-master/src/settings.py"
    $analyzer_init = "/etc/init.d/skyline-analyzer"
    $horizon_init = "/etc/init.d/skyline-horizon"
    $webapp_init = "/etc/init.d/skyline-webapp"

    # Ensure that the folders are present for skyline to run correctly
    file { [$log_path, $pid_path, $dump_dir]:
      ensure => 'directory',
      owner => $username,
      group => $group,
      mode => 755,
    }

    # Copy and install the skyline configuration file.
    file { $config_py:
        ensure  => present,
        content => template('/vagrant/templates/settings.py.erb'),
        require => $require_target,
        notify  => [Service['skyline-horizon'],Service['skyline-analyzer'],Service['skyline-webapp']],
    }
    # Copy and install the skyline analyzer init file.
    file { $analyzer_init:
        ensure  => present,
        content => template('/vagrant/templates/analyzer.init.erb'),
        owner => 'root',
        group => 'root',
        mode => 0755,
        require => $require_target,
    }
    # Copy and install the skyline horizon init file.
    file { $horizon_init:
        ensure  => present,
        content => template('/vagrant/templates/horizon.init.erb'),
        owner => 'root',
        group => 'root',
        mode => 0755,
        require => $require_target,
    }
    # Copy and install the skyline webapp init file.
    file { $webapp_init:
        ensure  => present,
        content => template('/vagrant/templates/webapp.init.erb'),
        owner => 'root',
        group => 'root',
        mode => 0755,
        require => $require_target,
    }
    # Change redis sock permissions if they are wrong.
    file { $redis_socket_path:
      mode => 775,
    }
    
    # Ensure services are running
    service { 'skyline-analyzer':
      ensure => 'running',
      enable => 'true',
      require => [File[$analyzer_init], Package[$pippackages], Package[$pipimportant]],
    }
    service { 'skyline-horizon':
      ensure => 'running',
      enable => 'true',
      require => [File[$horizon_init], Package[$pippackages], Package[$pipimportant]],
    }
    service { 'skyline-webapp':
      ensure => 'running',
      enable => 'true',
      require => [File[$webapp_init], Package[$pippackages], Package[$pipimportant]],
    }

}
