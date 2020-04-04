# service-oriented-architecture
READ-ME

############
INSTRUCTIONS
############

1. Clone the repo
2. Install necessary dependencies by performing the commands detailed in the INSTALLS section below.
3. In it you will find ngrok.exe, an application to access our website. Run two instances of ngrok and note the ports on which you run them. Further instructions to start ngrok can be found here: https://dashboard.ngrok.com/get-started.
4. Deploy the web application and back end components by performing the commands detailed in the DEPLOYMENT section below.
5. Run both python scripts (historic_prices.py and efficient_frontier.py). Make sure that the ports specified at the bottom of each script correspond to the port on which ngrok is running on.
6. Run the front end components (found here: https://github.com/Fadyazmy/cs4471).
7. Sign in. You can use this account, for example:
   Email: test@test.com
   Password: 123456
8. Play around with our services. To make sure you have full access to ALL our services, navigate to the User Profile page and set your name to Admin. This will give you full access to all services.
   Service 1: Stock Lookup (Displays historic prices for a given stock)
   Service 2: Efficient Frontier (Gives recommendations for a given portfolio)
   Service 3: Service Yellow Pages (Allows admins to control which services are available to users)

### Install ###
Python Dependencies:
$ pip install flask
$ pip install matplotlib
$ pip install numpy
$ pip install pandas
$ pip install yfinance
$ pip install firebase

Install NPM Dependencies:
$ npm i


### DEPLOYMENT ###
Host Back End Endpoint:
$ python historic_prices.py
$ python efficient_frontier.py

Deploy Front End:
$ npm build
$ firebase deploy
