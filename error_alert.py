import kavenegar

def error_sms_alert(api_key, message):
    kave_negar = kavenegar.KavenegarAPI(api_key)
    params = {
        "receptor": "09927417129",
        "message": message
    }
    response = kave_negar.sms_send(params)
    return response

def error_call_alert(api_key, message):
    kave_negar = kavenegar.KavenegarAPI(api_key)
    params = {
        "receptor": "09927417129",
        "message": message
    }
    response = kave_negar.call_maketts(params)
    return response
