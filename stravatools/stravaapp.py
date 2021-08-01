import requests

# Authentication URL
AUTH_URL = "https://www.strava.com/oauth/token"
# Access URL for activities
ACTIVITIES_URL = "https://www.strava.com/api/v3/athlete/activities"
# Access URL for activity
ACTIVITY_URL = "https://www.strava.com/api/v3/activities"
# webhooks subscription URL
SUBSCRIPTION_URL = "https://www.strava.com/api/v3/push_subscriptions"

class StravaApp(object):
    """
        Handler for a Strava application
    """
    def __init__(self, client_id, client_secret):
        """
            Constructor for StravaApp object

            :param client_id: ID of Strava application
            :param client_secret: secret code of Strava application
        """
        self._client_id = client_id
        self._client_secret = client_secret

    def get_token(self, refresh_token):
        """
            Request a Strava token

            :param refresh_token: refresh token of Strava application
            
            :return: access token for Strava application

        """
        payload = {
            'client_id': self._client_id,
            'client_secret': self._client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
            'f': 'json'
                }

        res = requests.post(AUTH_URL, data=payload)
        return res.json()['access_token']
    
    # TODO Set None for default value to before and after
    def get_activities(self, access_token, per_page, page, before=0, after=0):
        """
            Get a page of Strava activities
            
            :param access_token: access token for Strava application
            :param per_page: number of activities per page
            :param page: current page index
            :param before: ?????
            :param after: ?????
            
            :return: json containing array of activities
        """
        header = {'Authorization': 'Bearer ' + access_token}
        param = {'per_page': per_page, 'page': page}
        # TODO Test if following conditions are ensured
        if before:
            param['before'] = before
        if after:
            param['after'] = after
            
        res = requests.get(ACTIVITIES_URL, headers=header, params=param)
        return res.json()
    
    def get_activity(self, access_token, activity_id):
        """
            Get a Strava activity
            
            :param access_token: access token for Strava application
            :param activiy_id: ID of activity to return
            
            :return: strava activity
        """
        header = {'Authorization': 'Bearer ' + access_token}
        res = requests.get(ACTIVITY_URL+'/'+str(activity_id), headers=header)
        return res.json()
    
    def get_activity_streams(self, access_token, activity_id):
        """
            Get streams of a Strava activity
            
            :param access_token: access token for Strava application
            :param activity_id: ID of activity to return
            
            :return: Arrays of dictionnaries containing activity streams
        """
        header = {'Authorization': 'Bearer ' + access_token}
        keys = 'time,distance,watts,latlng,altitude,heartrate,temp,moving,cadence,grade_smooth,velocity_smooth'
        res = requests.get(ACTIVITY_URL+'/'+str(activity_id)+'/streams/'+str(keys), headers=header)
        return res.json()
    
    #def subscribe():
        #header = {'Authorization': 'Bearer ' + access_token}
        #param = {'client_id': self._client_id, 'client_secret': self._client_secret, 'callback_url': callback_url, ve}
                  
        
        
