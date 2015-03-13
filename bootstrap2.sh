sudo mkdir /var/run/skyline
sudo /opt/skyline/skyline-master/bin/horizon.d start
sudo /opt/skyline/skyline-master/bin/analyzer.d start
sudo /opt/skyline/skyline-master/bin/webapp.d start
sudo chmod +x /vagrant/gridpot-feeder/gridpot_feeder.py
sudo /vagrant/gridpot-feeder/gridpot_feeder.py