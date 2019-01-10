import logging
from django.conf import settings
from .models import SquareSettings
from oscar.apps.checkout.views import \
    PaymentDetailsView as OscarPaymentDetailsView, \
    ShippingAddressView as OscarShippingAddressView
from . import forms


logger = logging.getLogger('cart.checkout.views')


class PaymentDetailsView(OscarPaymentDetailsView):
    """
    Display the Square payment form during the Payment Details portion of th
    checkout process
    """

    def get_context_data(self, **kwargs):
        """
        Provide the square nonce form & application ID in the context dict
        """
        ctx = super().get_context_data(**kwargs)
        square_settings = SquareSettings.get_settings()

        ctx['square_form'] = kwargs.get('square_form', forms.SquareNonceForm())
        ctx['square_app'] = square_settings.application_id

        return ctx


    def handle_place_order_submission(self, request):
        """
        Handle Square payment form submission
        """
        submission = self.build_submission()

        #TODO: Is this check really necessary? Isn't it handled automatically by
        # Square's verification functions elsewhere?
        if submission['payment_kwargs']['nonce']:
            return self.submit(**submission)
        
        logger.info('handle_place_order_submission() called without card nonce')
        msg = ("There was a problem with our payment processor. Please try "
            "again in a few minutes, and contact us if this problem persists.")

        return self.render_payment_details(request, error=msg)


    def handle_payment_details_submission(self, request):
        """
        Handle Square payment form submission
        """
        square_form = forms.SquareNonceForm(request.POST)

        if square_form.is_valid():
            self.save_card_nonce(square_form.cleaned_data['nonce'])
            return self.render_preview(request)
        
        logger.info('handle_payment_details_submission() called without card nonce')
        msg = ("There was a problem with our payment processor. Please try "
            "again in a few minutes, and contact us if this problem persists.")

        return self.render_payment_details(request, error=msg, square_form=square_form)

