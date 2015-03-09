# -*- mode: ruby -*-
# # vi: set ft=ruby :
#
Vagrant.configure('2') do |config|
  config.vm.box = "puppetlabs/centos-7.0-64-puppet" #Built on fsalum/redis and gini/archive
1
  config.vm.network  "private_network", ip: "192.168.1.200"
  #config.vm.network "forwarded_port", guest: 1500, host: 1500

  config.vm.provider 'virtualbox' do |v|
    v.name = "Skyline"
    v.customize ["modifyvm", :id, "--memory", 1024]
    v.customize ["modifyvm", :id, "--cpus", 2]
	v.gui = false
  end
  Vagrant.configure("2") do |config|
    config.vm.provision "shell", path: "bootstrap.sh"
  end

  config.vm.provision :puppet do |puppet|
    puppet.manifests_path = "puppet/manifests"
    puppet.module_path    = "puppet/modules"
    puppet.manifest_file  = "init.pp"
    puppet.options = "--verbose --debug --trace"
  end
  Vagrant.configure("2") do |config|
    config.vm.provision "shell", path: "bootstrap2.sh"
  end
end
