import logging
logger = logging.getLogger()

HTTP_ERRORS = {
    'status_403': dict(status_code=403, reason='Authentication failed.'),
    'status_404': dict(status_code=404, reason='API not found.'),
    'status_405': dict(status_code=405, reason='Method not allowed.'),
    'status_406': dict(status_code=406, reason='No parameter or parameter type error.'),
    'status_501': dict(status_code=501, reason='Unable to parse JSON.')
}