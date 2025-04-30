from django.contrib.auth.tokens import PasswordResetTokenGenerator

class CustomerTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, customer, timestamp):
        return f"{customer.pk}{timestamp}{customer.password_hash}"

customer_token_generator = CustomerTokenGenerator()
