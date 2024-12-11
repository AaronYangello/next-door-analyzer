mkdir projects
cd projects
sudo apt update
sudo apt -y upgrade
python3 -V
sudo apt install -y python3-pip
pip install selenium
sudo apt install wget
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt-get install -f
wget https://chromedriver.storage.googleapis.com/111.0.5563.64/chromedriver_linux64.zip
sudo apt install unzip
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/bin/chromedriver
sudo chown root:root /usr/bin/chromedriver
sudo chmod +x /usr/bin/chromedriver
pip install selenium
pip install webdriver-manager