import datetime
import logging
from oscar.apps.checkout import mixins
from oscar.apps.payment.models import SourceType, Source
from oscar.apps.payment.exceptions import PaymentError, UnableToTakePayment
from oscar.core.loading import get_class
import squareconnect
from squareconnect.rest import ApiException
from squareconnect.apis.transactions_api import TransactionsApi
from .models import SquareSettings


logger = logging.getLogger('oscar_square.mixins')
api_instance = TransactionsApi()


class OrderPlacementMixin(mixins.OrderPlacementMixin):
    """
    Mixin which provides functionality for paying with SquareSpace
    """


    def handle_payment(self, order_number, total, **kwargs):
        """
        Try to process the payment using the Square REST API
        """
        square_settings = SquareSettings.get_settings()
        squareconnect.configuration.access_token = \
            square_settings.access_token
        source_type, __ = SourceType.objects.get_or_create(name='Square')
        source = Source(source_type=source_type,
                        amount_allocated=total.incl_tax)
        nonce = self.get_card_nonce()

        if not nonce:
            raise PaymentError('No card nonce provided')

        #TODO: Currency should be a setting stored in the settings model
        # Set the total amount to charge, in US Cents
        amount = {
            'amount': int(100*float(total.incl_tax)),
            'currency': 'USD'
        }

        #TODO: Delayed capture can be stored in settings, instead of static
        # Start the request for authorization, including shipping address and
        # user email (if provided)
        body = {
            'idempotency_key': self.get_idempotency_key(order_number),
            'card_nonce': nonce,
            'amount_money': amount,
            'delay_capture': True,
        }

        # Add user information for chargeback protection
        if 'email' in kwargs:
            body['buyer_email_address'] = kwargs['email']

        for addr_type in 'shipping_address', 'billing_address':
            if addr_type in kwargs:
                addr_object = kwargs[addr_type]
                address = dict()

                address['address_line_1'] = addr_object.line1
                address['address_line_2'] = addr_object.line2
                address['address_line_3'] = addr_object.line3
                address['locality'] = addr_object.line4
                address['administrative_district_level_1'] = addr_object.state
                address['postal_code'] = addr_object.postcode
                address['country'] = addr_object.country.iso_3166_1_a2
                address['first_name'] = addr_object.first_name
                address['last_name'] = addr_object.last_name

                body[addr_type] = address

        try:
            # Charge
            api_response = api_instance.charge(square_settings.location_id,
                    body)

            # Save the response ID
            if not api_response.transaction:
                raise ApiException(', '.join(api_response.errors))

        except ApiException as e:
            msg = "Exception when calling TransactionApi->charge: {}".format(e)
            logger.info(msg)
            raise PaymentError(msg) from ApiException

        # Request was successful - record the "payment source".  As this
        # request was a 'pre-auth', we set the 'amount_allocated' - if we had
        # performed an 'auth' request, then we would set 'amount_debited'.
        self.add_payment_source(source)

        #TODO: Change payment event type depending on delay/immediate capture
        # Also record payment event
        self.add_payment_event('auth', total.incl_tax,
                reference=api_response.transaction.id)


    def get_idempotency_key(self, order_number):
        """
        Returns an idempotency key based on the date and order number
        """
        today = datetime.date.today()
        return "{}_{}_auth".format(
                today.strftime('%Y%m%d'),
                order_number)


    def get_card_nonce(self):
        """
        Get the card payment nonce, and return an empty string if unset
        """
        return self.checkout_session._get('payment', 'nonce', '')


    def save_card_nonce(self, nonce):
        """
        Save the credit card payment nonce value to the session
        """
        self.checkout_session._set('payment', 'nonce', nonce)

