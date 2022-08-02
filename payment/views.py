from django.http import HttpResponseBadRequest
from django.shortcuts import render
from django.conf import settings
# Create your views here.
import razorpay
from django.views.decorators.csrf import csrf_exempt

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_ID, settings.RAZORPAY_SECRET_KEY))


def home(request):
    currency = 'INR'
    amount = 20000
    razorpay_order = razorpay_client.order.create(dict(amount=amount,
                                                       currency=currency,
                                                       payment_capture='1'))
    razorpay_order_id = razorpay_order['id']
    callback_url = 'http://127.0.0.1:8000/paymenthandler/'

    context = {}
    context['razorpay_order_id'] = razorpay_order_id
    context['razorpay_key'] = settings.RAZORPAY_ID
    context['razorpay_amount'] = amount
    context['currency'] = currency
    context['callback_url'] = callback_url
    return render(request, 'payment/index.html', context=context)


# we need to csrf_exempt this url as POST request will be made by Razorpay, and it won't have the csrf token.
@csrf_exempt
def paymenthandler(request):
    # only accept POST request.

    if request.method == "POST":
        try:
            # get the required parameters from post request.
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            # verify the payment signature.
            result = razorpay_client.utility.verify_payment_signature(params_dict)

            if result:
                amount = 20000  # Rs. 200
                # try:
                    # capture the payment
                    # razorpay_client.payment.capture(payment_id, amount)
                # print('success')
                    # render success page on successful capture of payment
                return render(request, 'payment/success.html')
                # except Exception as e:
                #     print(e, ', fail due to capture error')
                    # if there is an error while capturing payment.
                    # return render(request, 'payment/failure.html')
            else:
                print('Signature verification failed.')
                # if signature verification fails.
                return render(request, 'payment/failure.html')
        except Exception as e:
            print(e)
            # if we don't find the required parameters in POST data or we click the failure
            return render(request, 'payment/failure.html')
    else:
        # if other than POST request is made.
        return HttpResponseBadRequest()
