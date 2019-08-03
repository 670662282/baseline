import logging
logger = logging.getLogger()

HTTP_ERRORS = {
    'status_403': dict(status_code=403, reason='Authentication failed.'),
    'status_404': dict(status_code=404, reason='API not found.'),
    'status_405': dict(status_code=405, reason='Method not allowed.'),
    'status_406': dict(status_code=406, reason='No parameter or parameter type error.'),
    'status_501': dict(status_code=501, reason='Unable to parse JSON.')
}

OAUTH_APPS = {
    'baseline': {
        'app_id': 'c9ee1f76c8334a349e2830f591e5d8e6',
        'secret': '79059307819df2328b418447b9182420',
        'redirect_uri': '/baseline_api/api/oauth/baseline/callback'
    }
}

HELP_INFO = {
    "app.desc": '''In NBTD, you can select a group of protected network resources (Site, Network or Host).
     Then, select a time range. You can view the breakdown of protocols captured by the OP flow data analysis 
     and visualize them in charts that can be customized to display traffic baseline, detection policy settings 
     and recommended threshold values. 
     <br><br>The following legends are commonly seen in the Baseline View of each chart:
     <br><br>Actual Traffic - actual traffic of all protocols from flow data.<br>Baseline - 
     calculated traffic baseline from flow data of the last 30 days.<br>Actual High - 
     the upper threshold value defined by current <strong>Total Traffic</strong> policy.<br>
     Actual Low - the lower threshold value defined by current <strong>Total Traffic</strong> policy.
     <br>Recommended High - upper threshold value recommended for <strong>Total Traffic</strong> policy.<br>Recommended
      Low - lower threshold value recommended for <strong>Total Traffic</strong> policy.
    '''
}


