from handlers.api_not_found_handler import APINotFoundHandler
from handlers.help_Info_handler import HelpInfoHandler

BASE_ROUTES = {
    'baseline': [
        (r'/api/baseline/customer/.*', HelpInfoHandler),
        (r'/api/baseline/help/.*', HelpInfoHandler),
        (r'/api/baseline/settings/.*', HelpInfoHandler),
        (r'/api/baseline/baseline/.*', HelpInfoHandler),
        (r'/api/baseline/traffic/.*', HelpInfoHandler),
        (r'/api/baseline/uninstall/.*', HelpInfoHandler),
        (r'/api/test/.*', HelpInfoHandler),
        (r'/.*', APINotFoundHandler),
    ],
}
