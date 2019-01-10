import logging
from django.core.urlresolvers import reverse
from oscar.apps.checkout import exceptions, session


logger = logging.getLogger('cart.checkout.session')


class CheckoutSessionMixin(session.CheckoutSessionMixin):
    """
    Implement tax and payment-related functionality specific to our site
    """

    def build_submission(self, **kwargs):
        """
        Collate all order data required for a submission
        """
        submission = super().build_submission(**kwargs)

        # If a shipping address is present, add it to the payment kwargs to
        # submit to Square (required for chargeback protection)
        if submission['shipping_address'] and submission['shipping_method']:
            submission['payment_kwargs']['shipping_address'] = submission['shipping_address']

        # Add user email to the payment kwargs (required for chargeback
        # protection; billing_address is already sent into the payment kwargs)
        if 'user' in submission and hasattr(submission['user'], 'email'):
            submission['payment_kwargs']['email']= submission['user'].email
        elif 'guest_email' in submission:
            submission['payment_kwargs']['email'] = submission['guest_email']

        # Send along the card nonce retrieved in previous steps
        submission['payment_kwargs']['nonce'] = self.get_card_nonce()

        return submission


    def check_payment_data_is_captured(self, request):
        """
        Validate that we have a card nonce stored from Square
        """

        # Check to make sure we have a nonce from the payment processor
        if not self.get_card_nonce():
            msg = "We're sorry, we could not contact the payment processor."
            raise exceptions.FailedPreCondition(
                    url=reverse('checkout:payment-details'),
                    message=msg)

        # Run parent function; currently doesn't do anything, but may be
        # implemented in the future
        super().check_payment_data_is_captured(request)

