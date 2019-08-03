# -*- coding: utf-8 -*-


SERVER_ERROR = {'code': 50000, 'msg': 'Server error.'}
NOT_FOUND = {'code': 50001, 'msg': 'Not found.'}
PARAM_NOT_FOUND = {'code': 50002, 'msg': 'Requested parameter not found.'}
PARAM_INVALID = {'code': 50003, 'msg': 'Parameter invalid.'}
ALREADY_OAUTH = {'code': 50004, 'msg': 'Already authorized.'}
SIGNATURE_INVALID = {'code': 50005, 'msg': 'Signature invalid.'}
NOT_OAUTH = {'code': 50006, 'msg': 'Not authorized.'}
REMOTE_SERVER_ERROR = {'code': 50007, 'msg': 'Remote server error.'}

SETTINGS_DATA_NOT_FOUND = {'code': 50008, 'msg': 'Settings data not found.'}

CUSTOMER_ID_NOT_FOUND = {'code': 50009, 'msg': 'Customer id is required.'}
ALGORITHM_NOT_FOUND = {'code': 50010, 'msg': 'Algorithm is required.'}
ALGORITHM_NAME_ERROR = {'code': 50011, 'msg': 'Algorithm must be one of 3sigma or LSTM.'}

THRESHOLD_TYPE_NOT_FOUND = {'code': 50012, 'msg': 'Threshold type is required.'}
THRESHOLD_TYPE_ERROR = {'code': 50012, 'msg': 'Threshold type is invalid'}
THRESHOLD_TIMES_NOT_FOUND = {'code': 50013, 'msg': 'Threshold times is required.'}
THRESHOLD_TIMES_RANGE = {'code': 50014, 'msg': 'Threshold times must be a number greater than 0 and in the range 0-100.'}

UPLINK_VALIDATE_ERROR_MSG = {'code': 50015, 'msg': 'Uplink must be a positive number and support K/M/G suffix format.'}

CUSTOMER_PROFILE_NOT_FOUND = {'code': 50016, 'msg': 'Customer profile not found.'}

