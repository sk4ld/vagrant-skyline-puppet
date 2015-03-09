sudo yum install -y epel-release
sudo cp /vagrant/pip.rb /usr/share/ruby/vendor_ruby/puppet/provider/package/.
sudo cp /vagrant/redis.conf /etc/.
sudo chmod 755 /var/dump/
puppet module install fsalum-redis --modulepath=puppet/modules 
puppet module install gini-archive --modulepath=puppet/modules 
sudo dos2unix /etc/rc.d/init.d/skyline-analyzer
sudo dos2unix /etc/rc.d/init.d/skyline-horizon
sudo dos2unix /etc/rc.d/init.d/skyline-webapp
