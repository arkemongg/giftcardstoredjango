from django.http import HttpResponse
import json
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
import hmac
import hashlib
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def hello(request):
    return HttpResponse("Hi")






# COINBASE_WEBHOOK_SECRET = settings.COINBASE_HOOK

# @csrf_exempt
# def coinbase_webhook(request):
#     if request.method == 'POST':
#         signature = request.headers.get('X-CC-Webhook-Signature', '')
#         if not verify_coinbase_signature(signature, request.body):
#             return HttpResponseBadRequest('Invalid signature')
#         payload = json.loads(request.body)
#         print(payload)
#         print(payload['event']['type'])

#         return HttpResponse(status=200)
#     else:
#         return HttpResponseBadRequest('Invalid request method')

# def verify_coinbase_signature(signature, payload):
#     secret_bytes = bytes(COINBASE_WEBHOOK_SECRET, 'utf-8')
#     expected_signature = hmac.new(secret_bytes, payload, hashlib.sha256).hexdigest()
#     return hmac.compare_digest(signature, expected_signature)

# data = {
#     'attempt_number': 1,
#     'event': {
#         'api_version': '2018-03-22',
#         'created_at': '2023-05-30T21:12:02Z',
#         'data': {
#             'id': 'eb4304c7-fa58-435e-96d0-3ee33a8ec4ff',
#             'code': '4ML425A4',
#             'name': 'a',
#             'utxo': False,
#             'pricing': {
#                 'dai': {'amount': '9.999500024998750062', 'currency': 'DAI'},
#                 'usdc': {'amount': '10.000000', 'currency': 'USDC'},
#                 'local': {'amount': '10.00', 'currency': 'USD'},
#                 'pusdc': {'amount': '10.000000', 'currency': 'PUSDC'},
#                 'pweth': {'amount': '0.005242450216382133', 'currency': 'PWETH'},
#                 'tether': {'amount': '9.996151', 'currency': 'USDT'},
#                 'apecoin': {'amount': '3.130870381966186600', 'currency': 'APE'},
#                 'bitcoin': {'amount': '0.00035961', 'currency': 'BTC'},
#                 'polygon': {'amount': '11.046672000', 'currency': 'PMATIC'},
#                 'dogecoin': {'amount': '138.15016923', 'currency': 'DOGE'},
#                 'ethereum': {'amount': '0.005245000', 'currency': 'ETH'},
#                 'litecoin': {'amount': '0.10871338', 'currency': 'LTC'},
#                 'shibainu': {'amount': '1148765.077541640000000000', 'currency': 'SHIB'},
#                 'bitcoincash': {'amount': '0.08716496', 'currency': 'BCH'}
#             },
#             'checkout': {'id': '978efce3-3b95-489d-9c83-6f1cd7b70ed2'},
#             'fee_rate': 0.01,
#             'logo_url': '',
#             'metadata': {'name': '12'},
#             'payments': [],
#             'resource': 'charge',
#             'timeline': [{'time': '2023-05-30T21:12:02Z', 'status': 'NEW'}],
#             'addresses': {
#                 'dai': '0xcb266d923f6bf06c11e5580b6b31aaf4e48e3db6',
#                 'usdc': '0xcb266d923f6bf06c11e5580b6b31aaf4e48e3db6',
#                 'pusdc': '0xcb266d923f6bf06c11e5580b6b31aaf4e48e3db6',
#                 'pweth': '0xcb266d923f6bf06c11e5580b6b31aaf4e48e3db6',
#                 'tether': '0xcb266d923f6bf06c11e5580b6b31aaf4e48e3db6',
#                 'apecoin': '0xcb266d923f6bf06c11e5580b6b31aaf4e48e3db6',
#                 'bitcoin': '33GcLGi4W27obtvp2V6MfjphNfPJgpSPLd',
#                 'polygon': '0xcb266d923f6bf06c11e5580b6b31aaf4e48e3db6',
#                 'dogecoin': 'DU5eouoRioKHP779wV3fRFWndWwtcw7X7C',
#                 'ethereum': '0xcb266d923f6bf06c11e5580b6b31aaf4e48e3db6',
#                 'litecoin': 'MGtdKea8oSjdRa7Nd2FfxdcSGdhu72MZW6',
#                 'shibainu': '0xcb266d923f6bf06c11e5580b6b31aaf4e48e3db6',
#                 'bitcoincash': 'qqnaw9k0yyg7vms4c6nuv72ujk2jkxt5vg9tyw9mwc'
#             },
#             'pwcb_only': False,
#             'created_at': '2023-05-30T21:12:02Z',
#             'expires_at': '2023-05-30T22:12:02Z',
#             'hosted_url': 'https://commerce.coinbase.com/charges/4ML425A4',
#             'brand_color': '#122332',
#             'description': '5',
#             'fees_settled': True,
#             'pricing_type': 'fixed_price',
#             'support_email': 'ark.emon596@gmail.com',
#             'brand_logo_url': '',
#             'exchange_rates': {
#                 'APE-USD': '3.194',
#                 'BCH-USD': '114.725',
#                 'BTC-USD': '27808.09',
#                 'DAI-USD': '1.00005',
#                 'ETH-USD': '1906.755',
#                 'LTC-USD': '91.985',
#                 'DOGE-USD': '0.072385',
#                 'SHIB-USD': '0.000008705',
#                 'USDC-USD': '1.0',
#                 'USDT-USD': '1.000385',
#                 'PUSDC-USD': '1.0',
#                 'PWETH-USD': '1907.505',
#                 'PMATIC-USD': '0.90525'
#             },
#             'offchain_eligible': False,
#             'organization_name': '',
#             'payment_threshold': {
#                 'overpayment_absolute_threshold': {'amount': '5.00', 'currency': 'USD'},
#                 'overpayment_relative_threshold': '0.005',
#                 'underpayment_absolute_threshold': {'amount': '5.00', 'currency': 'USD'},
#                 'underpayment_relative_threshold': '0.005'
#             },
#             'local_exchange_rates': {
#                 'APE-USD': '3.194',
#                 'BCH-USD': '114.725',
#                 'BTC-USD': '27808.09',
#                 'DAI-USD': '1.00005',
#                 'ETH-USD': '1906.755',
#                 'LTC-USD': '91.985',
#                 'DOGE-USD': '0.072385',
#                 'SHIB-USD': '0.000008705',
#                 'USDC-USD': '1.0',
#                 'USDT-USD': '1.000385',
#                 'PUSDC-USD': '1.0',
#                 'PWETH-USD': '1907.505',
#                 'PMATIC-USD': '0.90525'
#             },
#             'coinbase_managed_merchant': False
#         },
#         'id': '845f8016-57ce-4b87-9299-3df6138eb2f6',
#         'resource': 'event',
#         'type': 'charge:created'
#     },
#     'id': '2cf56bd1-5742-4823-8445-d6be56e9653f',
#     'scheduled_for': '2023-05-30T21:12:02Z'
# }