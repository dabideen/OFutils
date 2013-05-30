#!/bin/sh
#
# This script installs CPqD ofsoftswitch13 and trema-edge on Ubuntu 12.04 64bit LTS server (kernel 2.6.x).
#
export PATH=$PATH:/sbin:/bin:/usr/sbin:/usr/bin

# Install OFutils
sudo cp ~/OFutils/print-ftable.py /usr/bin/ & EPID=$!
wait $EPID
sudo chmod 777 /usr/bin/print-ftable.py & EPID=$!
wait $EPID
sudo cp ~/OFutils/start-switch.py /usr/bin/ & EPID=$!
wait $EPID
sudo chmod 777 /usr/bin/start-switch.py & EPID=$!
wait $EPID

if [ ! -f "~/OF" ]; then
        mkdir ~/OF
        cd ~/OF

        sudo apt-get update& EPID=$!
        wait $EPID
        # No upgrade because it will bring up a dialog for GRUB (grub-pc)
        #sudo apt-get -y  upgrade& EPID=$!
        #wait $EPID
        #sudo apt-get -y  dist-upgrade& EPID=$!
        #wait $EPID

        ## Install git.
        sudo apt-get -y install \
	    git-core unzip cmake libpcap-dev libxerces-c2-dev libpcre3-dev flex \
	    bison g++ autoconf libtool pkg-config libboost-all-dev gawk screen & EPID=$!
        wait $EPID

        # Install Netbee
        ## Fetch the latest code of Netbee.
        sudo wget -q http://www.nbee.org/download/nbeesrc-12-05-16.php & EPID=$!
        wait $EPID
        sudo mv nbeesrc-12-05-16.php nbeesrc-12-05-16.zip & EPID=$!
        wait $EPID
        sudo unzip -q nbeesrc-12-05-16.zip & EPID=$!
        wait $EPID
        cd nbeesrc/src/ 
        sudo cmake . & EPID=$!
        wait $EPID
        sudo make & EPID=$!
        wait $EPID
        sudo cp ../bin/libnb*.so /usr/local/lib
        sudo ldconfig & EPID=$!
        wait $EPID
        sudo cp ../include/*.h /usr/include
        cd ~/OF

        # Install of13softswitch 
        ## Fetch the latest software switch code.
        sudo git clone https://github.com/dabideen/ofsoftswitch13.git & EPID=$!
        wait $EPID
        cd ofsoftswitch13 
        sudo ./boot.sh & EPID=$!
        wait $EPID
        sudo ./configure & EPID=$!
        wait $EPID
        sudo make & EPID=$!
        wait $EPID
        sudo make install & EPID=$!
        wait $EPID
        cd ~/OF & EPID=$!
        wait $EPID
        sudo ln -s ~/OF/ofsoftswitch13/udatapath/ofdatapath /usr/bin/ & EPID=$!
        wait $EPID
        sudo chmod 777 /usr/bin/ofdatapath & EPID=$!
        wait $EPID
        sudo ln -s ~/OF/ofsoftswitch13/secchan/ofprotocol /usr/bin/ & EPID=$!
        wait $EPID
        sudo chmod 777 /usr/bin/ofprotocol & EPID=$!
        wait $EPID
        
        
        # Install trema-edge
        #sudo git clone https://github.com/dabideen/trema-edge.git & EPID=$!
        #wait $EPID
        #sudo apt-get install -y gcc make ruby1.8 rubygems1.8 ruby1.8-dev libpcap-dev libsqlite3-dev & EPID=$!
        #wait $EPID
        #sudo gem install bundler & EPID=$!
        #wait $EPID
        #cd trema-edge
        #sudo bundle install & EPID=$!
        #wait $EPID
        #sudo ./build.rb & EPID=$!
        #wait $EPID

        sudo chmod 777 -R ~/OF  & EPID=$!
        wait $EPID

         

        #Disable IPv6.
	cat <<EOF | sudo tee -a /etc/sysctl.conf
# Disable IPv6
net.ipv6.conf.all.disable_ipv6 = 1
net.ipv6.conf.default.disable_ipv6 = 1
net.ipv6.conf.lo.disable_ipv6 = 1
EOF

        ## Reboot the OS to run a latest kernel without IPv6.
        sudo reboot
fi

